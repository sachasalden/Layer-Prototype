import asyncio
from layers.presentation import (
    PresentationProtocol,
    send_message,
    read_messages,
    error_message
)

class HanTTPSessionClient:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port

    async def start(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        buffer = ""

        # Handshake
        await send_message(writer, {
            "type": "join",
            "version": 1,
            "payload": {"playerId": "P1"}
        })

        # Wacht op handshake-ack
        while True:
            data = await reader.read(1024)
            buffer += data.decode()
            messages, buffer = read_messages(buffer)

            for msg in messages:
                print("Ontvangen:", msg)
                return reader, writer, buffer
