class Validator:
    @staticmethod
    def validateMessage(data):
        if not isinstance(data,dict):
            return {"error":"invalid data"}
        if "type" not in data:
            return {"error":"invalid data"}
        if not isinstance(data["type"],str):
            return {"error":"invalid data"}
        return None

