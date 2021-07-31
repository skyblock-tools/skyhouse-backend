import runtimeConfig

import json


def read_config(path: str) -> None:
    with open(path) as f:
        config = json.load(f)
        runtimeConfig.mongodb_connection_string = config["mongodb_connection_string"]
        runtimeConfig.initial_cogs = config["initial_cogs"]
