# this shows the allowed versions so that deprecated versions aren't allowed
SUPPORTED_VERSION = 1

# here you can define what is mandatory in certain messages (currently examples)
MESSAGE_SCHEMAS = {
    "move": {"playerId", "x", "y"},
    "shoot": {"playerId", "direction"},
    "join": {"playerId"},
    "leave": {"playerId"},
    "ping": set(),
    "pong": set(),
    # server → client
    "state_update": {"players", "items", "timestamp"},
    "error": {"code", "details"},
}

# returns an error message
def error_message(code: str, details: str):
    return {
        "type": "error",
        "version": SUPPORTED_VERSION,
        "payload": {"code": code, "details": details},
    }