import asyncio
import threading
import flask

import runtimeConfig
from cogs.api.middleware.auth_ratelimit import auth_ratelimit
from utils import auction_filter


def setup():
    app: flask.Flask = flask.Flask(__name__)

    @app.route('/flips')
    @auth_ratelimit
    async def flips(session):
        _filter = auction_filter.parse_filter(flask.request.args)
        keys = runtimeConfig.redis.keys("binflip:*")
        pipeline = runtimeConfig.redis.pipeline()
        for key in keys:
            pipeline.hgetall(key)
        result = pipeline.execute()
        _flips = {}
        for x in result:
            _flips[x['uuid']] = {"profit": x['profit'], "quantity": x["quantity"]}
        pipeline = runtimeConfig.redis.pipeline()
        for flip in _flips:
            pipeline.hgetall(f"auction:{flip}")
        result = pipeline.execute()
        for x in result:
            if not x:
                continue
            if auction_filter.include(_flips[x['uuid']] | x, _filter):
                _flips[x['uuid']].update(x)
        return {"flips": _flips, "refresh_session": session.active}

    runtimeConfig.app = app
    thread: threading.Thread = threading.Thread(target=app.run)
    thread.setDaemon(True)
    thread.start()
