class Handlers:
    def handlePing(data):
        return "PING"
    def handlePong(data):
        return "PONG"

    def handleEcho(data):
        return {"type": "echo_response", "message": data.get("message", "")}
    def handleError(data):
        return "ERROR"

    def handle_login(data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "missing_credentials"}

        return {"type": "login_ok", "user": username}