import importlib

from flask import Flask

import runtimeConfig
import configReader


CONFIG_NAME: str = "config.json"

configReader.read_config(CONFIG_NAME)

app: Flask = Flask(__name__)
runtimeConfig.app = app

runtimeConfig.loaded_cogs = {}
for cog_path in runtimeConfig.initial_cogs:
    cog = importlib.import_module(cog_path)
    cog.on_enable()
    runtimeConfig.loaded_cogs[cog_path] = cog

if __name__ == '__main__':
    app.run()
