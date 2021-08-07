from flask import request
import runtimeConfig
import time

from utils.JsonWrapper import JsonWrapper

no_success = {"success": False}


def auth_ratelimit(func):  # noqa
    async def inner(*args, **kwargs):
        header = request.headers.get("Authorization")
        if not header or not header.startswith("Bearer "):
            return no_success, 401
        token = header.split("Bearer ")[1]
        session = runtimeConfig.redis.hgetall(f"session:{token}")
        if not session:
            return no_success, 401
        session = JsonWrapper.from_dict(session)
        session.active = True
        if session.minute_start + 60 < time.time():
            session.minute_start = round(time.time())
            session.uses_minute = session.uses_minute + 1
            session.total_uses = session.total_uses + 1
        else:
            if session.uses_minute > session.ratelimit:
                return no_success, 429, {"Retry-After": session.minute_start + 60 - time.time()}
            else:
                session.uses_minute = session.uses_minute + 1
                session.total_uses = session.total_uses + 1
        if False:  # TODO: auto-delete sessions after [] requests or time
            runtimeConfig.redis.delete(f"session:{token}")
            session.active = False

        runtimeConfig.redis.hset(f"session:{token}", mapping=session)

        return await func(session, *args, **kwargs)

    return inner
