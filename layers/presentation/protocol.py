import json
from typing import Dict, Any, Tuple, List
from .presentation import SUPPORTED_VERSION, MESSAGE_SCHEMAS, error_message

class PresentationProtocol:

# validates the message
    @staticmethod
    def validate_message(msg: Dict[str, Any]):
        # checks if message is an instance of a dictionary
        if not isinstance(msg, dict):
            return "NOT_OBJECT"
        # checks if the message has component mentioned below
        if "type" not in msg or "version" not in msg or "payload" not in msg:
            return "INVALID_FORMAT"

        # checsk if the message type is known
        typ = msg["type"]
        if typ not in MESSAGE_SCHEMAS:
            return "UNKNOWN_TYPE"

        # loads what is required in the message and checks if the payload is a dictionary
        required = MESSAGE_SCHEMAS[typ]
        payload = msg.get("payload", {})
        if not isinstance(payload, dict):
            return "INVALID_PAYLOAD"

        # returns the required fields that are missing in the payload
        missing = required - set(payload.keys())
        if missing:
            return f"MISSING_FIELDS:{','.join(sorted(missing))}"

        # checks for the version and if it is supported
        if not isinstance(msg["version"], int):
            return "INVALID_VERSION"
        if msg["version"] != SUPPORTED_VERSION:
            return "UNSUPPORTED_VERSION"

        return None


async def send_message(writer, msg: Dict[str, Any]):
    # removes unnecessary spaces to reduce the used bandwidth
    line = json.dumps(msg, separators=(",", ":")) + "\n"
    # converts the msg into bytes
    writer.write(line.encode("utf-8"))
    # makes sure that the data is sent
    await writer.drain()


def read_messages(buffer: str) -> Tuple[List[Dict[str, Any]], str]:
    # list of all messages from the buffer
    messages = []
    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        #skips empty messages
        if not line.strip():
            continue
        #converts json into python if it fails append an error message
        try:
            msg = json.loads(line)
        except Exception:
            messages.append(error_message("INVALID_JSON", "Could not parse JSON"))
            continue
        #adds it to the message list if the json is valid
        messages.append(msg)
    return messages, buffer