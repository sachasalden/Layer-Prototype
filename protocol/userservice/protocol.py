import json

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
