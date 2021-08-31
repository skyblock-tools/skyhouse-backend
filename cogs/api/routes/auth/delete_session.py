import time

import flask
from ...utils import cors, res

import runtimeConfig


def setup(app: flask.Flask):
    @app.route("/auth/token/close")
    @cors.site_only()
    def delete_session_endpoint():
        query = flask.request.args
        web_token = query.get("webtoken", None)
        mod_token = query.get("modtoken", None)
        token_type = "web" if web_token is not None else "mod"
        token = web_token if web_token is not None else mod_token

        if token is None:
            return res.json(code=401)

        doc = runtimeConfig.mongodb_user_collection.find_one({f"{token_type}_refresh_token": token})
        if not doc:
            return res.json(code=403)

        update = {f"{token_type}_session_token": None}
        if token_type == "web":
            update |= {"web_refresh_token": None, "web_refresh_token_generated": -time.time()}

        runtimeConfig.mongodb_user_collection.update_one(doc, {"$set": update})
        return res.json({"success": True})
