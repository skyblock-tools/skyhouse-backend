from flask import request
import runtimeConfig
import time
import functools

from utils import misc
from utils.JsonWrapper import JsonWrapper
from ..utils import res

no_success = {"success": False}


def auth_ratelimit(ratelimit=True):  # noqa

    def inner(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization")
            if not header or not header.startswith("Bearer "):
                return res.json(code=401)
            token = header.split("Bearer ")[1]
            session = runtimeConfig.redis.hgetall(f"session:{token}")
            if not session:
                return res.json(code=401)
            session = JsonWrapper.from_dict(session)
            session.parse_str_ints()
            session.active = True

            if ratelimit:
                if session.minute_start + 60 < time.time():
                    session.minute_start = round(time.time())
                    session.uses_minute = 0
                    session.total_uses = session.total_uses + 1
                else:
                    if session.uses_minute > session.ratelimit:
                        return res.json(code=429, headers={"Retry-After": round(session.minute_start + 60 - time.time()) + 1})
                    else:
                        session.uses_minute = session.uses_minute + 1
                        session.total_uses = session.total_uses + 1
                if session.total_uses > 60 or session.created + 600 < time.time():
                    runtimeConfig.redis.delete(f"session:{token}")  # noqa
                    session.active = False

                runtimeConfig.redis.hset(f"session:{token}", mapping=misc.redis_json_dump(session.to_dict()))

            return func(session, *args, **kwargs)

        return wrapper

    return inner
