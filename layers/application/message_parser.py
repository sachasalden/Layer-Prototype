import json
from json import JSONDecodeError


class MessageParser:
    def parse(rawData:str):
        try:
            return json.loads(rawData)
        except JSONDecodeError:
            return {"error":"JSON niet okayy"}


