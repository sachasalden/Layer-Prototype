import json
from .message_parser import MessageParser
from ..presentation.presentation import error_message
from .response_builder import ResponseBuilder
from .application_router import ApplicationRouter
from .validate import Validator


class ApplicationLayer:

    async def process(self, raw: str) -> str:
        data = MessageParser.parse(raw)

        if "error" in data:
            return ResponseBuilder.build(error_message(400, data["error"], "/"))

        validation_error = Validator.validateMessage(data)
        if validation_error:
            return ResponseBuilder.build(error_message(400, validation_error, data.get("resource", "/")))

        response = await ApplicationRouter.route(data)

        return ResponseBuilder.build(response)
