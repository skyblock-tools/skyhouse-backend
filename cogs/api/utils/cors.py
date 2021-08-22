import functools
from flask import make_response, request

import runtimeConfig


def site_only(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        res = make_response()
        if request.method == "OPTIONS":
            res.headers.add("Access-Control-Allow-Origin", runtimeConfig.cors_host)
            res.headers.add("Access-Control-Allow-Headers", runtimeConfig.cors_host)
            res.headers.add("Access-Control-Allow-Methods", runtimeConfig.cors_host)
            return res
        else:
            result = func(*args, **kwargs)
        if "Access-Control-Allow-Origin" not in result.headers:
            result.headers.add("Access-Control-Allow-Origin", runtimeConfig.cors_host)
        return result

    return inner
