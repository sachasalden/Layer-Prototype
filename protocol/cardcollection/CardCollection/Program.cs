using DefaultNamespace;

class Program
{
    static async Task Main(string[] args)
    {
        string host = Environment.GetEnvironmentVariable("HOST") ?? "0.0.0.0";
        int port = int.Parse(Environment.GetEnvironmentVariable("PORT") ?? "4001");

        var server = new CardCollectionServer(host, port);
        await server.Start();
    }
}