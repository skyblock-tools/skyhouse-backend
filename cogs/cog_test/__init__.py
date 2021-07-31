import runtimeConfig

import atexit

from flask import Flask


def on_enable():
    app: Flask = runtimeConfig.app

    @app.route("/")
    def index():
        return "Hello, world!"


@atexit.register
def on_disable():
    print("cog_test exits")
