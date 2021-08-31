import flask
import runtimeConfig
from cogs.api.middleware.auth_ratelimit import auth_ratelimit
from cogs.api.utils import cors, res


def setup(app: flask.Flask):
    @app.route('/auth/token/info')
    @cors.site_only()
    @auth_ratelimit(ratelimit=False)
    def auth_info_endpoint(session):
        discord_id = session.discord_user_id
        doc = runtimeConfig.mongodb_user_collection.find_one({"_id": str(discord_id)})
        if not doc:
            return res.json(code=401)
        return res.json({
            "mod_refresh_token": doc["mod_refresh_token"],
            "privilege_level": doc["privilege_level"],
            "discord_id": discord_id,
        })
