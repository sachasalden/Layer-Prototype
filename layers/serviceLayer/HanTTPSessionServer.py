import socket
import asyncio
from layers.presentation import (
    PresentationProtocol,
    read_messages,
    send_message,
    error_message
)

class HanTTPSessionServer:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print("Server gestart op", self.host, self.port)
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        print("Client verbonden.")
        buffer = ""

        # Handshake fase
        buffer = await self.handle_handshake(reader, writer, buffer)

        # Sessie fase → normaal verkeer
        print("Sessielaag actief.")
        while True:
            data = await reader.read(1024)
            if not data:
                print("Client afgesloten.")
                break

            buffer += data.decode()
            messages, buffer = read_messages(buffer)

            for msg in messages:

                #Validate message
                error = PresentationProtocol.validate_message(msg)
                if error:
                    await send_message(writer, error_message(error, "Invalid message"))
                    continue

                # Handle types
                if msg["type"] == "ping":
                    await send_message(writer, {"type": "pong", "version": 1, "payload": {}})

    async def handle_handshake(self, reader, writer, buffer):
        while True:
            data = await reader.read(1024)
            if not data:
                break

            buffer += data.decode()
            messages, buffer = read_messages(buffer)

            for msg in messages:
                error = PresentationProtocol.validate_message(msg)
                if error:
                    await send_message(writer, error_message(error, "Invalid handshake"))
                    continue

                if msg["type"] == "join":
                    print("Handshake ontvangen.")
                    await send_message(writer, {
                        "type": "state_update",
                        "version": 1,
                        "payload": {"players": [], "items": [], "timestamp": 0}
                    })
                    return buffer
