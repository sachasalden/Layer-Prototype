import asyncio
import json
from ..presentation.presentation import error_message
from .service_registry import SERVICE_REGISTRY


class ApplicationRouter:

    @staticmethod
    async def route(msg):
        resource = msg["resource"]

        # match resource to microservice
        if resource not in SERVICE_REGISTRY:
            return error_message(404, "Resource not found", resource)

        host, port = SERVICE_REGISTRY[resource]

        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.write((json.dumps(msg) + "\n").encode())
            await writer.drain()

            resp_raw = await reader.readline()
            writer.close()
            await writer.wait_closed()

            return json.loads(resp_raw.decode())

        except Exception as e:
            return error_message(503, "Service Unavailable: " + str(e), resource)
