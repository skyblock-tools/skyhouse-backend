import threading

import flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import importlib
from loguru import logger

import runtimeConfig
from cogs.api.middleware.auth_ratelimit import auth_ratelimit


def setup():

    api_app: flask.Flask = flask.Flask(__name__)
    app = DispatcherMiddleware(flask.Flask("dummy_app"), {
        "/api": api_app,
    })

    routes = ['flip', 'auth.token_exchange', 'auth.delete_session', 'auth.info', 'auth.oauth.discord_oauth']

    for route in routes:
        module = importlib.import_module(f"cogs.api.routes.{route}")
        # noinspection PyUnresolvedReferences
        module.setup(api_app)

    runtimeConfig.app = app

    def start():
        from waitress import serve
        serve(app, port=8000)

    thread: threading.Thread = threading.Thread(target=start)
    thread.setDaemon(True)
    thread.start()
