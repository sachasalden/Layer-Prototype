import asyncio
from shared.protocol import send_message, read_messages

class Client:
    def __init__(self, host="127.0.0.1", port=4000):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.buffer = ""

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def send(self, resource, action, payload):
        await send_message(self.writer, {
            "resource": resource,
            "action": action,
            "payload": payload
        })

        while True:
            data = await self.reader.read(1024)
            self.buffer += data.decode()
            messages, self.buffer = read_messages(self.buffer)
            if messages:
                return messages[0]


async def main():
    client = Client()
    await client.connect()
    resp = await client.send("/user", "login", {"username": "x", "password": "y"})
    print(resp)

asyncio.run(main())
