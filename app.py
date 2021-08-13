import importlib
import os

import runtimeConfig
import configReader
from utils import logging
from loguru import logger

CONFIG_NAME: str = "base_config.json"

configReader.read_config(CONFIG_NAME)


def main():
    logging.init_logging()
    runtimeConfig.loaded_cogs = {}
    for cog_path in runtimeConfig.initial_cogs:
        logger.info(f"loading {cog_path}")
        try:
            cog = importlib.import_module(cog_path)
            # noinspection PyUnresolvedReferences
            cog.setup()
            runtimeConfig.loaded_cogs[cog_path] = cog
            logger.info(f"successfully loaded {cog_path}")
        except:  # noqa E721
            logger.exception(f"Error loading {cog_path}")

    while True:
        pass


if __name__ == '__main__':
    main()
