import flask

import cogs.core.craftflip_engine
from ..middleware.auth_ratelimit import auth_ratelimit
from ..utils import cors, res
from ...core.craftflip_engine import craftflips


def setup(app: flask.Flask):
    @app.route('/craftflips')
    @cors.site_only()
    @auth_ratelimit()
    def craftflip_endpoint(session):
        if session.privilege_level < 4:
            return res.json(code=403)
        return res.json({"craftflips": cogs.core.craftflip_engine.craftflips, "refresh_session": not session.active})