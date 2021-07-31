import importlib

from flask import Flask

import runtimeConfig
import configReader


CONFIG_NAME: str = "config.json"

app: Flask = Flask(__name__)

runtimeConfig.app = app

configReader.read_config(CONFIG_NAME)


def reload_cogs():
    for cog in runtimeConfig.initial_cogs:
        module = importlib.import_module(cog)
        module.run()


reload_cogs()


@app.route("/admin/reload_config")
def api_reload_config():
    configReader.read_config(CONFIG_NAME)
    return "Reloaded"


@app.route("/admin/reload_cogs")
def api_reload_cogs():
    reload_cogs()
    return "Reloaded"


if __name__ == '__main__':
    app.run()
