import asyncio
from protocol import send_message, parse_messages
from service_registry import SERVICES
import os

class Gateway:
    def __init__(self, host="127.0.0.1", port=4000):
        self.host = host
        self.port = port

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        buffer = ""

        while True:
            data = await reader.read(1024)
            if not data:
                break

            buffer += data.decode()
            messages, buffer = parse_messages(buffer)

            for msg in messages:
                asyncio.create_task(self.forward(msg, writer))

    async def forward(self, msg, client_writer):
        resource = msg["resource"]
        action = msg["action"]
        host, port = SERVICES.get(resource, (None, None))

        if host is None:
            resp = {
                "id": msg["id"],
                "status": 404,
                "resource": resource,
                "payload": {"error": "unknown resource"}
            }
            await send_message(client_writer, resp)
            return

        service_reader, service_writer = await asyncio.open_connection(host, port)
        await send_message(service_writer, msg)

        data = await service_reader.read(1024)
        service_msgs, _ = parse_messages(data.decode())

        await send_message(client_writer, service_msgs[0])
        service_writer.close()

if __name__ == "__main__":
    gw = Gateway(host=os.getenv("HOST", "0.0.0.0"),
                 port=int(os.getenv("PORT", "4000")))

    asyncio.run(gw.start())
