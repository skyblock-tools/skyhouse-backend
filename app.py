import importlib
import os

import runtimeConfig
import configReader

CONFIG_NAME: str = "base_config.json"

configReader.read_config(CONFIG_NAME)


def main():
    runtimeConfig.loaded_cogs = {}
    for cog_path in runtimeConfig.initial_cogs:
        cog = importlib.import_module(cog_path)
        # noinspection PyUnresolvedReferences
        cog.setup()
        runtimeConfig.loaded_cogs[cog_path] = cog
    while True:
        try:
            pass
        except KeyboardInterrupt:
            os._exit(130)  # noqa


if __name__ == '__main__':
    main()
