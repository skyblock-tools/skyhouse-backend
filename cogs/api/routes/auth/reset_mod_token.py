import flask
import runtimeConfig
from cogs.api.middleware.auth_ratelimit import auth_ratelimit
from utils.misc import generate_token


def setup(app: flask.Flask):

    @app.route('/auth/token/reset', methods=["POST", "DELETE"])
    @auth_ratelimit(ratelimit=False)
    def auth_reset_endpoint(session):
        discord_id = session.discord_user_id
        new = generate_token()
        runtimeConfig.mongodb_user_collection.update_one({"_id": str(discord_id)}, {"$set": {"mod_refresh_token": new}})
        return {
            "mod_refresh_token": new,
        }
