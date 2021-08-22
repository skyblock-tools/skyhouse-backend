import os
import sys

import loguru
import logging


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def convert_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(InterceptHandler())


# noinspection SpellCheckingInspection
def init_logging():
    if os.environ.get("shenv") != "development":
        loguru.logger.configure(handlers=[{"sink": sys.stderr, "level": "INFO"}])
    loguru.logger.add("skyhouse.log", enqueue=True, level="DEBUG")

    convert_logger("waitress")
    convert_logger("discord_webhook")
