import asyncio
from shared.protocol import read_messages, send_message, error_message
from battleengine.battle_engine import BattleEngine


class BattleEngineServer:
    def __init__(self, host="127.0.0.1", port=6002):
        self.host = host
        self.port = port
        self.engine = BattleEngine()

    async def start(self):
        server = await asyncio.start_server(self.handle, self.host, self.port)
        async with server:
            await server.serve_forever()

    async def handle(self, reader, writer):
        buffer = ""

        while True:
            data = await reader.read(1024)
            if not data:
                break

            buffer += data.decode()
            messages, buffer = read_messages(buffer)

            for msg in messages:
                action = msg.get("action")
                payload = msg.get("payload", {})

                if not action or not hasattr(self.engine, action):
                    resp = error_message(400, "/battle", "Unknown action")
                else:
                    method = getattr(self.engine, action)
                    resp = await method(payload)

                await send_message(writer, resp)


if __name__ == "__main__":
    asyncio.run(BattleEngineServer().start())
