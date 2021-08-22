import flask
import runtimeConfig
from cogs.api.middleware.auth_ratelimit import auth_ratelimit


def setup(app: flask.Flask):

    @app.route('/auth/token/info')
    @auth_ratelimit(ratelimit=False)
    def auth_info_endpoint(session):
        discord_id = session.discord_user_id
        doc = runtimeConfig.mongodb_user_collection.find_one({"_id": str(discord_id)})
        return {
            "mod_refresh_token": doc["mod_refresh_token"],
            "privilege_level": doc["privilege_level"],
            "discord_id": discord_id,
        }
