namespace DefaultNamespace;
using System.Threading.Tasks;

public class CardCollectionService
{
    public async Task<object> SaveCardAsync(object payload, string resource)
    {
        await Task.Delay(500);

        return new
        {
            status = 200,
            resource = resource,
            payload = new
            {
                message = "Card saved successfully",
                name = "Fire Dragon",
                hp = 120,
                power = 40,
                cost = 3,
                description = "A powerful flame-based dragon.",
                image = "fire_dragon.png"
            }
        };
    }
}