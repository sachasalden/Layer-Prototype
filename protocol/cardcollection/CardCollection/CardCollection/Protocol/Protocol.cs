using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace DefaultNamespace
{
    public static class Protocol
    {
        private static readonly JsonSerializerOptions JsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = false
        };

        // Encode object to JSON + newline (send_message)
        public static byte[] EncodeMessage(object message)
        {
            string json = JsonSerializer.Serialize(message, JsonOptions) + "\n";
            return Encoding.UTF8.GetBytes(json);
        }

        // Parse messages from buffer (\n separated)
        public static List<Dictionary<string, object>> ParseMessages(ref string buffer)
        {
            var messages = new List<Dictionary<string, object>>();

            while (buffer.Contains('\n'))
            {
                int idx = buffer.IndexOf('\n');
                string line = buffer.Substring(0, idx);
                buffer = buffer.Substring(idx + 1);

                if (string.IsNullOrWhiteSpace(line)) continue;

                try
                {
                    var msg = JsonSerializer.Deserialize<Dictionary<string, object>>(line, JsonOptions);
                    messages.Add(msg);
                }
                catch
                {
                    messages.Add(ErrorMessage(400, "/", "INVALID_JSON"));
                }
            }

            return messages;
        }

        // Create error message like Python error_message()
        public static Dictionary<string, object> ErrorMessage(int status, string resource, string reason)
        {
            return new Dictionary<string, object>
            {
                { "status", status },
                { "resource", resource },
                { "payload", new Dictionary<string, object> { { "error", reason } } }
            };
        }
    }
}