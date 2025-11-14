from .message_parser import MessageParser
from .handlers import Handlers
from .metadata import MetaData
from .response_builder import ResponseBuilder
from .validate import Validator
class ApplicationLayer:
    def process(self,raw):
        data = MessageParser.parse(raw)
        meta = MetaData.generate(data)

        if "error" in data:
            meta["status"] = "error"
            return ResponseBuilder.build({"meta":meta,"data":data})

        validationError= Validator.validateMessage(data)
        if validationError:
            meta["status"] = "error"
            return ResponseBuilder.build({"meta":meta,"data":data})


        messageType = data["type"]
        if messageType == "ping":
            response = Handlers.handlePing(data)

        elif messageType == "pong":
            response = Handlers.handlePong(data)
        elif messageType == "echo_response":
            response = Handlers.handleEcho(data)

        else:
            response = Handlers.handleError(data)

        return ResponseBuilder.build({"meta":meta,"data":response})