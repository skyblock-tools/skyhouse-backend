import flask_cors

import runtimeConfig


def site_only():
    return flask_cors.cross_origin(
        origins=runtimeConfig.cors_host,
        supports_credentials=True,
    )
