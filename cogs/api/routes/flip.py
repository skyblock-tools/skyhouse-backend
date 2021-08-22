import time

import flask
import random

from utils.JsonWrapper import JsonWrapper
from ..middleware.auth_ratelimit import auth_ratelimit
from utils import auction_filter
import runtimeConfig
from ..utils import cors, res
from ...core.auction import get_api_output


def setup(app: flask.Flask):
    @app.route('/flips')
    @cors.site_only
    @auth_ratelimit()
    def flip_endpoint(session):
        if session.privilege_level < 1:
            return res.json(code=403)
        _filter = auction_filter.parse_filter(flask.request.args, priv=session.privilege_level > 1, level=session.privilege_level)
        _filter.parse_str_ints()
        if session.privilege_level < 2:
            _filter.bin_max_profit = 500_000
        keys = runtimeConfig.redis.keys("*flip:*")
        pipeline = runtimeConfig.redis.pipeline()
        _flips = {}
        for key in keys:
            pipeline.hgetall(key)
        result = pipeline.execute()
        _flips = {}
        for x in result:
            _flips[x['uuid']] = {"profit": x['profit'], "quantity": x["quantity"], "type": x["type"]}
        pipeline = runtimeConfig.redis.pipeline()
        for flip in _flips:
            pipeline.hgetall(f"{_flips[flip]['type']}:{flip}")
        result = pipeline.execute()
        output = []
        result.sort(key=lambda z: -1 if "uuid" not in z else int(_flips[z['uuid']]['profit']), reverse=True)
        for x in result:
            if not x:
                continue
            if len(output) >= _filter.limit:
                break
            tmp = JsonWrapper.from_dict(_flips[x["uuid"]] | x)
            tmp.parse_str_ints()
            if tmp.type == "auction" and tmp.end / 1000 - time.time() > 300:
                continue
            if auction_filter.include(tmp, _filter):
                out = JsonWrapper.from_dict(get_api_output(_flips[x["uuid"]] | x))
                out.parse_str_ints()
                output.append(out.to_dict())
        return res.json({"flips": output, "refresh_session": not session.active})

