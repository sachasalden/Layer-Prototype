import asyncio, uuid
from protocol.shared.protocol import send_message, parse_messages

class Client:
    def __init__(self, host="127.0.0.1", port=4000):
        self.host = host
        self.port = port
        self.buffer = ""
        self.pending = {}  # id → Future

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        asyncio.create_task(self.listen())

    async def listen(self):
        while True:
            data = await self.reader.read(1024)
            if not data:
                break

            self.buffer += data.decode()
            messages, self.buffer = parse_messages(self.buffer)

            for msg in messages:
                req_id = msg["id"]
                if req_id in self.pending:
                    self.pending[req_id].set_result(msg)

    async def send(self, resource, action, payload):
        req_id = str(uuid.uuid4())

        future = asyncio.get_event_loop().create_future()
        self.pending[req_id] = future

        await send_message(self.writer, {
            "id": req_id,
            "resource": resource,
            "action": action,
            "payload": payload
        })

        return await future


async def main():
    c = Client()
    await c.connect()

    t2 = c.send("/user", "login", {})
    t3 = c.send("/card", "savecard", {})
    t4 = c.send("/battle", "playedcard", {})


    print(await t2)
    print(await t3)
    print(await t4)

asyncio.run(main())
