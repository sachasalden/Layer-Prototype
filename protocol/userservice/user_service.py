import asyncio


class UserService:
    async def login(self, payload, resource):
        await asyncio.sleep(0.5)
        return {
            "status": 200,
            "resource": resource,
            "payload": {"token": "xyz-123"}
        }

    async def waittest(self, payload, resource):
        await asyncio.sleep(5)
        return {
            "status": 200,
            "resource": resource,
            "payload": {"done": True}
        }
