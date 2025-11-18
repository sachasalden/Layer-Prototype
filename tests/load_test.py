import asyncio
import random
import time
from shared.protocol import send_message, read_messages


class TestClient:
    def __init__(self, name, host="127.0.0.1", port=4000):
        self.name = name
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.buffer = ""

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def request(self, resource, action, payload):
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

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()



async def test_single_calls():
    print("\n--- test_single_calls ---")
    client = TestClient("single")
    await client.connect()

    print(await client.request("/user", "login", {"username": "x", "password": "y"}))
    print(await client.request("/user", "register", {"username": "x2", "password": "y2"}))
    print(await client.request("/user", "get_user", {}))

    await client.close()



async def test_parallel_logins(n=10):
    print("\n--- test_parallel_logins ---")
    clients = [TestClient(f"C{i}") for i in range(n)]
    await asyncio.gather(*[c.connect() for c in clients])

    async def do_login(c: TestClient):
        return await c.request("/user", "login", {"username": c.name, "password": "123"})

    results = await asyncio.gather(*[do_login(c) for c in clients])
    for r in results:
        print(r)

    await asyncio.gather(*[c.close() for c in clients])



async def test_100_requests():
    print("\n--- test_100_requests ---")
    client = TestClient("mass")
    await client.connect()

    for i in range(100):
        resp = await client.request("/user", "login", {"username": f"user{i}", "password": "pw"})
        print(f"{i}: {resp}")

    await client.close()



async def test_100_parallel_requests():
    print("\n--- test_100_parallel_requests ---")
    clients = [TestClient(f"C{i}") for i in range(100)]
    await asyncio.gather(*[c.connect() for c in clients])

    async def mock(c: TestClient):
        return await c.request("/user", "login", {"username": c.name, "password": "pw"})

    results = await asyncio.gather(*[mock(c) for c in clients])
    print("DONE 100 parallel")

    await asyncio.gather(*[c.close() for c in clients])



async def stress_test(duration=5):
    print("\n--- stress_test running ---")
    start = time.time()

    clients = [TestClient(f"s{i}") for i in range(20)]
    await asyncio.gather(*[c.connect() for c in clients])

    async def random_request(c: TestClient):
        while time.time() - start < duration:
            action = random.choice(["login", "register", "get_user"])
            payload = {"username": c.name, "password": "pw"}
            await c.request("/user", action, payload)
            await asyncio.sleep(random.random() * 0.2)

    tasks = [random_request(c) for c in clients]
    await asyncio.gather(*tasks)

    await asyncio.gather(*[c.close() for c in clients])
    print("STRESS TEST DONE")




async def main():
    await test_single_calls()
    await test_parallel_logins(10)
    await test_100_requests()
    await test_100_parallel_requests()
    await stress_test(duration=5)

asyncio.run(main())
