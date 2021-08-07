import asyncio
import threading
import flask

import runtimeConfig
from cogs.api.middleware.auth_ratelimit import auth_ratelimit


def setup():
    app: flask.Flask = flask.Flask(__name__)

    @app.route('/flips')
    @auth_ratelimit
    async def flips(session):
        keys = runtimeConfig.redis.keys("binflip:*")
        pipeline = runtimeConfig.redis.pipeline()
        for key in keys:
            pipeline.hgetall(key)
        result = pipeline.execute()
        _flips = {}
        for x in result:
            _flips[x['uuid']] = {"profit": x['profit'], "data": None}
        pipeline = runtimeConfig.redis.pipeline()
        for flip in _flips:
            pipeline.hgetall(f"auction:{flip}")
        result = pipeline.execute()
        for x in result:
            if not x:
                continue
            _flips[x['uuid']]['data'] = x
        return {"flips": _flips, "refresh_session": session.active}

    runtimeConfig.app = app
    thread: threading.Thread = threading.Thread(target=app.run)
    thread.setDaemon(True)
    thread.start()
