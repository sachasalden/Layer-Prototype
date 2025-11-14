from .message_parser import MessageParser
from .handlers import Handlers
from .metadata import MetaData
from .response_builder import ResponseBuilder
from .validate import Validator

class ApplicationLayer:

    def process(self, raw: str) -> str:
        meta = MetaData.generate(raw)

        data = MessageParser.parse(raw)

        if "error" in data:
            meta["status"] = "error"
            return ResponseBuilder.build({
                "meta": meta,
                "data": data
            })

        validation_error = Validator.validateMessage(data)
        if validation_error:
            meta["status"] = "error"
            return ResponseBuilder.build({
                "meta": meta,
                "data": validation_error
            })

        msg_type = data["type"]

        if msg_type == "ping":
            response = Handlers.handlePing(data)

        elif msg_type == "echo":
            response = Handlers.handleEcho(data)

        elif msg_type == "login":
            response = Handlers.handleLogin(data)

        else:
            response = Handlers.handleUnknown(data)
            meta["status"] = "error"

        return ResponseBuilder.build({
            "meta": meta,
            "data": response
        })
