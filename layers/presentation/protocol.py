import json
from typing import Dict, Any, Tuple, List
from .presentation import MESSAGE_SCHEMAS, VALID_METHODS, SUPPORTED_VERSION, error_message


class PresentationProtocol:

    @staticmethod
    def validate_message(msg: Dict[str, Any]):
        if not isinstance(msg, dict):
            return "NOT_OBJECT"

        if "method" in msg:
            kind = "REQUEST"
        elif "status" in msg:
            kind = "RESPONSE"
        else:
            return "INVALID_STRUCTURE"

        required = MESSAGE_SCHEMAS[kind]
        missing = required - set(msg.keys())
        if missing:
            return f"MISSING_FIELDS:{','.join(missing)}"

        if kind == "REQUEST":
            if msg["method"] not in VALID_METHODS:
                return "INVALID_METHOD"
            if not isinstance(msg["resource"], str):
                return "INVALID_RESOURCE"

        if kind == "RESPONSE":
            if not isinstance(msg["status"], int):
                return "INVALID_STATUS"

        return None


async def send_message(writer, msg: Dict[str, Any]):
    line = json.dumps(msg, separators=(",", ":")) + "\n"
    writer.write(line.encode("utf-8"))
    await writer.drain()


def read_messages(buffer: str) -> Tuple[List[Dict[str, Any]], str]:
    messages = []
    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except:
            messages.append(error_message(400, "INVALID_JSON", "/"))
            continue
        messages.append(msg)
    return messages, buffer
