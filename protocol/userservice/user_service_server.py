import asyncio
from protocol import send_message, parse_messages
from user_service import UserService

import os
class UserServiceServer:
    def __init__(self):
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "6001"))

        self.service = UserService()
        # routes om de action te linken aan een functie
        self.routes = {
            "login": self.service.login,
            "waittest": self.service.waittest
        }

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
                asyncio.create_task(self.process_message(msg, writer))

    async def process_message(self, msg, writer):
        # van de gateway krijg je een ID, action, resource en payload. ID is voor het bijhouden wie welke request heeft gestuurd en de response linken
        # aan de goede request. action is voor het linken met de service function. zo kan de server weten welke service functie hij moet callen
        # de resource is voor de gateway voor het kiezen welke service hij heen moet
        # de payload is voor de service voor de business logica
        req_id = msg["id"]
        action = msg.get("action")
        resource = msg.get("resource")
        payload = msg.get("payload", {})

        if action not in self.routes:
            resp = {
                "id": req_id,
                "status": 400,
                "resource": resource,
                "payload": {"error": "unknown action"}
            }
        else:
            handler = self.routes[action]
            result = await handler(payload, resource)
            resp = {"id": req_id, **result}

        await send_message(writer, resp)


if __name__ == "__main__":
    server = UserServiceServer()
    asyncio.run(server.start())
