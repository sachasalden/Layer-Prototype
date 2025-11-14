from .message_parser import MessageParser
from .handlers import Handlers
from .response_builder import ResponseBuilder

class ApplicationLayer:
    def process(self,raw):
        data = MessageParser.parse(raw)
        if "type" not in data:
            return ResponseBuilder.build({"error":"no type given"})
        messageType = data["type"]
        if messageType == "ping":
            response = Handlers.handlePing(data)

        elif messageType == "pong":
            response = Handlers.handlePong(data)
        elif messageType == "echo_response":
            response = Handlers.handleEcho(data)

        else:
            response = Handlers.handleError(data)

        return ResponseBuilder.build(response)