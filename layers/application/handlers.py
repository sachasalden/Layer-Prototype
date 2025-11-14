class Handlers:

    @staticmethod
    def handlePing(data):
        return {
            "type": "pong"
        }

    @staticmethod
    def handleEcho(data):
        return {
            "type": "echo_response",
            "message": data.get("message", "")
        }

    @staticmethod
    def handleLogin(data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "missing_credentials"}

        return {
            "type": "login_ok",
            "user": username
        }

    @staticmethod
    def handleUnknown(data):
        return {
            "error": "unknown_message_type"
        }
