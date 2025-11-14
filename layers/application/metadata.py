import time
import uuid
class MetaData:
    @staticmethod
    def generate(data):
        return {
            "messageId": str(uuid.uuid4()),
            "timestamp": time.time(),
            "protocol":"1.0",
            "size": len(data),
            "status":"OK"
        }