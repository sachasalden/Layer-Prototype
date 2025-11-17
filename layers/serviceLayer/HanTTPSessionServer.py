import asyncio
import json
from ..presentation.protocol import PresentationProtocol, read_messages, send_message, error_message
from ..application.application_layer import ApplicationLayer


class HanTTPSessionServer:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        buffer = ""
        app = ApplicationLayer()

        while True:
            data = await reader.read(1024)
            if not data:
                break

            buffer += data.decode()
            messages, buffer = read_messages(buffer)

            for msg in messages:
                error = PresentationProtocol.validate_message(msg)
                if error:
                    resp = error_message(400, error, msg.get("resource", "/"))
                    await send_message(writer, resp)
                    continue

                response_json = await app.process(json.dumps(msg))
                response = json.loads(response_json)

                await send_message(writer, response)
