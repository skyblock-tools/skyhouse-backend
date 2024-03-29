import time

import flask

from utils.JsonWrapper import JsonWrapper
from ..middleware.auth_ratelimit import auth_ratelimit
from utils import auction_filter
import runtimeConfig
from ..utils import cors, res
from ...core.auction import get_api_output


def setup(app: flask.Flask):
    @app.route('/flips')
    @cors.site_only()
    @auth_ratelimit()
    def flip_endpoint(session):
        if session.privilege_level < 1:
            return res.json(code=403)
        _filter = auction_filter.parse_filter(flask.request.args, priv=session.privilege_level > 1,
                                              level=session.privilege_level)
        _filter.parse_str_ints()
        if session.privilege_level < 2:
            _filter.bin_max_profit = 1_000_000
        keys = runtimeConfig.redis.keys("*flip:*")
        pipeline = runtimeConfig.redis.pipeline()
        _flips = {}
        for key in keys:
            pipeline.hgetall(key)
        result = pipeline.execute()
        _flips = {}
        for i, x in enumerate(result):
            if "uuid" in x:
                _flips[x['uuid']] = {"profit": x.get('profit', 0), "quantity": x.get("quantity", 0),
                                     "type": x.get("type", ""),
                                     "i_name": keys[i].split(":")[1], "resell_price": x.get("resell_price", 0)}
        pipeline = runtimeConfig.redis.pipeline()
        for flip in _flips:
            pipeline.hgetall(f"{_flips[flip]['type']}:{_flips[flip]['i_name']}:{flip}")
        result = pipeline.execute()
        output = []
        result = [*filter(lambda z: "uuid" in z, result)]

        if _filter.sort == auction_filter.SORT_PROFIT_PROPORTION:
            result.sort(key=lambda z: int(_flips[z['uuid']]['profit']) / int(z["price"]), reverse=True)
        elif _filter.sort == auction_filter.SORT_PRICE:
            result.sort(key=lambda z: int(z["price"]))
        elif _filter.sort == auction_filter.SORT_QUANTITY:
            result.sort(key=lambda z: int(_flips[z["uuid"]]["quantity"]), reverse=True)
        else:
            result.sort(key=lambda z: int(_flips[z['uuid']]['profit']), reverse=True)

        for x in result:
            if not x:
                continue
            if len(output) >= _filter.limit:
                break
            tmp = JsonWrapper.from_dict(_flips[x["uuid"]] | x)
            tmp.parse_str_ints()
            if tmp.type == "auction" and tmp.end - time.time() > 300:
                continue
            if auction_filter.include(tmp, _filter):
                out = JsonWrapper.from_dict(get_api_output(_flips[x["uuid"]] | x))
                out.parse_str_ints()
                output.append(out.to_dict())
        return res.json({"flips": output, "refresh_session": not session.active})
