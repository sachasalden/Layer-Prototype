using DefaultNamespace;

class Program
{
    static async Task Main(string[] args)
    {
        var server = new CardCollectionServer("127.0.0.1", 4001);
        await server.Start();
    }
}