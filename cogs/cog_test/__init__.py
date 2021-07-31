import runtimeConfig

from flask import Flask


def run():
    app: Flask = runtimeConfig.app

    @app.route("/")
    def index():
        return "Hello, world!"
