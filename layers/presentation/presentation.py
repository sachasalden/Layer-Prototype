SUPPORTED_VERSION = 1

MESSAGE_SCHEMAS = {
    "REQUEST": {"method", "resource", "payload"},
    "RESPONSE": {"status", "resource", "payload"},
}

VALID_METHODS = {"GET", "POST", "PUT", "DELETE"}

def error_message(status: int, message: str, resource: str):
    return {
        "status": status,
        "resource": resource,
        "payload": {"error": message}
    }
