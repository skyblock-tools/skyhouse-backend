import uuid
import json


def generate_token():
    return str(uuid.uuid4()).lower().replace("-", "")


def redis_json_dump(obj: dict):
    return {k: v if type(v) in [str, int, float] else json.dumps(v) for k, v in obj.items()}
