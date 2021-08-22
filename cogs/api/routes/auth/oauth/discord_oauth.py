import time

import requests
import flask

import runtimeConfig
from utils import payloads, misc
from utils.JsonWrapper import JsonWrapper
from utils.constants import API
from utils.misc import generate_token
from ....utils import cors, res

API_ENDPOINT = 'https://discord.com/api/v8'


def exchange_code(code, redirect_uri):
    data = {
        'client_id': runtimeConfig.discord_oauth["client_id"],
        'client_secret': runtimeConfig.discord_oauth["client_secret"],
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
    return r.json()


def auth_request(endpoint, access_token) -> JsonWrapper or list:
    resp = requests.get(f"{API_ENDPOINT}/{endpoint}", headers={
        "Authorization": f"Bearer {access_token}",
    }).json()
    if isinstance(resp, dict):
        return JsonWrapper.from_dict(resp)
    else:
        return resp


def get_user(access_token):
    return auth_request("users/@me", access_token)


def get_user_guilds(access_token):
    return auth_request("users/@me/guilds", access_token)


def setup(app: flask.Flask):
    @cors.site_only
    @app.route('/auth/oauth/discord')
    def discord_oauth_endpoint():
        query = flask.request.args
        code = query.get("code", None)
        redirect_uri = query.get("redirect_uri", runtimeConfig.discord_oauth["redirect_uri"])
        if code is None:
            return res.json(code=401)
        discord_access_token = exchange_code(code, redirect_uri).get("access_token", None)
        if discord_access_token is None:
            return res.json(code=403)
        user, guilds = get_user(discord_access_token), get_user_guilds(discord_access_token)

        current_user = runtimeConfig.mongodb_user_collection.find_one({"_id": str(user["id"])})
        web_refresh_token = generate_token()
        access_token = generate_token()

        in_guild = False
        for guild in guilds:
            if guild["id"] == str(runtimeConfig.discord_guild_id):
                in_guild = True
                break
        privilege = 1 if in_guild else 0
        if not current_user:
            rate_limit = API.RATE_LIMITS[privilege]
            payload = payloads.user_payload(user["id"], privilege_level=privilege, ratelimit_minute=rate_limit,
                                            web_refresh_token=web_refresh_token, session_token=access_token)
        else:
            if current_user["web_refresh_token_generated"] < 0 and current_user["web_refresh_token_generated"] + time.time() < 15: # noqa
                return res.json(code=403)
            if current_user["session_token"] is not None:
                uses_minute_str = runtimeConfig.redis.hget(f"session:{current_user['session_token']}", "uses_minute")
                if uses_minute_str is not None and int(uses_minute_str) > 1:
                    return res.json(code=403)
            rate_limit = current_user.get("ratelimit_minute", 0)
            if in_guild:
                privilege = max(privilege, current_user.get("privilege_level", 0))
                rate_limit = max(API.RATE_LIMITS[privilege], rate_limit)
            runtimeConfig.mongodb_user_collection.update_one(current_user, {"$set": {
                "web_refresh_token_generated": time.time(),
                "privilege_level": privilege,
                "ratelimit_minute": rate_limit,
                "session_token": access_token,
            }})
        session = {
            "discord_user_id": user["id"],
            "refresh_token": web_refresh_token,
            "privilege_level": privilege,
            "ratelimit": rate_limit, # noqa
            "uses_minute": 0,
            "minute_start": round(time.time()),
            "total_uses": 0,
            "created": round(time.time()),
        }
        runtimeConfig.redis.hset(f"session:{access_token}", mapping=misc.redis_json_dump(session))
        return res.json({
            "access_token": access_token,
            "privilege_level": privilege,
            "refresh_token": web_refresh_token,
            "discord_info": user.to_dict(),
               })

