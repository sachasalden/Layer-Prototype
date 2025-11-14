class Handlers:
    def handlePing(data):
        return "PING"
    def handlePong(data):
        return "PONG"

    def handleEcho(data):
        return {"type": "echo_response", "message": data.get("message", "")}
    def handleError(data):
        return "ERROR"
