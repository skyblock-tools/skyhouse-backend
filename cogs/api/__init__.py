import threading
import flask

import runtimeConfig


def setup():
    app: flask.Flask = flask.Flask(__name__)
    runtimeConfig.app = app
    thread: threading.Thread = threading.Thread(target=app.run)
    thread.setDaemon(True)
    thread.start()
