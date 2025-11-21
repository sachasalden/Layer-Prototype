using System.Net;
using System.Net.Sockets;
using System.Text;

namespace DefaultNamespace
{
    public class CardCollectionServer
    {
        private readonly TcpListener listener;
        private readonly CardCollectionService service;
        private readonly Dictionary<string, Func<object, string, Task<object>>> routes;

        public CardCollectionServer(string host = "127.0.0.1", int port = 4001)
        {
            listener = new TcpListener(IPAddress.Parse(host), port);
            service = new CardCollectionService();

            routes = new Dictionary<string, Func<object, string, Task<object>>>
            {
                { "savecard", service.SaveCardAsync }
            };
        }

        public async Task Start()
        {
            listener.Start();
            Console.WriteLine("[CardCollectionServer] Running...");

            while (true)
            {
                var client = await listener.AcceptTcpClientAsync();
                _ = HandleClient(client);
            }
        }

        private async Task HandleClient(TcpClient client)
        {
            var stream = client.GetStream();
            string buffer = "";
            byte[] temp = new byte[1024];

            Console.WriteLine("[CardCollectionServer] Client connected!");

            while (client.Connected)
            {
                int read = await stream.ReadAsync(temp, 0, temp.Length);
                if (read == 0) break;

                buffer += Encoding.UTF8.GetString(temp, 0, read);

                var messages = Protocol.ParseMessages(ref buffer);

                foreach (var msg in messages)
                {
                    _ = ProcessMessage(msg, stream);
                }
            }

            Console.WriteLine("[CardCollectionServer] Client disconnected.");
        }

        private async Task ProcessMessage(Dictionary<string, object> msg, NetworkStream stream)
        {
            string reqId = msg["id"].ToString();
            string action = msg["action"].ToString();
            string resource = msg["resource"].ToString();
            object payload = msg.ContainsKey("payload") ? msg["payload"] : new { };

            object response;

            if (!routes.ContainsKey(action))
            {
                response = new
                {
                    id = reqId,
                    status = 400,
                    resource = resource,
                    payload = new { error = "unknown action" }
                };
            }
            else
            {
                var handler = routes[action];
                var serviceResponse = await handler(payload, resource);

                response = new
                {
                    id = reqId,
                    status = (int)serviceResponse.GetType().GetProperty("status")?.GetValue(serviceResponse),
                    resource = serviceResponse.GetType().GetProperty("resource")?.GetValue(serviceResponse),
                    payload = serviceResponse.GetType().GetProperty("payload")?.GetValue(serviceResponse)
                };
            }

            byte[] data = Protocol.EncodeMessage(response);
            await stream.WriteAsync(data, 0, data.Length);
        }
    }
}
