import time
import flask

import runtimeConfig
from utils import misc
from utils.misc import generate_token
from ...utils import cors, res


def setup(app: flask.Flask):
    @app.route("/auth/token/create")
    @cors.site_only()
    def token_exchange_endpoint():
        query = flask.request.args
        web_token = query.get("webtoken", None)
        mod_token = query.get("modtoken", None)
        token_type = "web" if web_token is not None else "mod"
        token = web_token if web_token is not None else mod_token

        if token is None:
            return res.json(code=401)

        doc = runtimeConfig.mongodb_user_collection.find_one({f"{token_type}_refresh_token": token})
        if not doc:
            return res.json(code=401)

        if token_type == "web" and doc["web_refresh_token_generated"] < 0 and doc[
            "web_refresh_token_generated"] + time.time() < 15:  # noqa
            return res.json(code=403)

        if doc[f"{token_type}_session_token"] is not None:
            current_session = runtimeConfig.redis.hgetall(f"session:{doc[f'{token_type}_session_token']}")
            if current_session and "uses_minute" in current_session and int(current_session["uses_minute"]) > 1 and int(
                    current_session["minute_start"]) + 60 > time.time():
                return res.json(code=403)

        session_id = generate_token()

        session = {
            "discord_user_id": doc["_id"],
            "privilege_level": doc["privilege_level"],
            "ratelimit": doc["ratelimit_minute"],
            "minute_start": round(time.time()),
            "uses_minute": 0,
            "total_uses": 0,
            "created": round(time.time()),
        }
        response = {}
        if token_type == "web":
            if doc["web_refresh_token_generated"] + 2_592_000 < time.time():
                return res.json(code=403)
            refresh_token = generate_token()
            response["refresh_token"] = refresh_token
            runtimeConfig.mongodb_user_collection.update_one(doc, {"$set": {
                "web_refresh_token": refresh_token
            }})
        runtimeConfig.mongodb_user_collection.update_one({"_id": doc["_id"]}, {"$set": {f"{token_type}_session_token": session_id}})

        runtimeConfig.redis.delete(f"session:{doc[f'{token_type}_session_token']}")
        runtimeConfig.redis.hset(f"session:{session_id}", mapping=misc.redis_json_dump(session))
        response["access_token"] = session_id
        response["privilege_level"] = doc["privilege_level"]
        return res.json(response)
