import json

MESSAGE_REQUEST = {"action", "resource", "payload"}
MESSAGE_RESPONSE = {"status", "resource", "payload"}

VALID_METHODS = {"GET", "POST", "PUT", "DELETE"}

def validate(msg):
    if not isinstance(msg, dict):
        return "NOT_OBJECT"
    if "method" in msg:
        missing = MESSAGE_REQUEST - set(msg.keys())
        if missing:
            return "MISSING_FIELDS"
        if msg["method"] not in VALID_METHODS:
            return "INVALID_METHOD"
        if not isinstance(msg["resource"], str):
            return "INVALID_RESOURCE"
    elif "status" in msg:
        missing = MESSAGE_RESPONSE - set(msg.keys())
        if missing:
            return "MISSING_FIELDS"
        if not isinstance(msg["status"], int):
            return "INVALID_STATUS"
    else:
        return "INVALID_STRUCTURE"
    return None

def error_message(status, resource, reason):
    return {"status": status, "resource": resource, "payload": {"error": reason}}

async def send_message(writer, msg):
    writer.write((json.dumps(msg) + "\n").encode())
    await writer.drain()

def parse_messages(buffer):
    messages = []
    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        if line.strip():
            messages.append(json.loads(line))
    return messages, buffer

def read_messages(buffer):
    messages = []
    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        if line.strip():
            try:
                messages.append(json.loads(line))
            except:
                messages.append(error_message(400, "/", "INVALID_JSON"))
    return messages, buffer
