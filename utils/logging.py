import os
import sys

import loguru


# noinspection SpellCheckingInspection
def init_logging():
    if os.environ.get("shenv") != "development":
        loguru.logger.configure(handlers=[{"sink": sys.stderr, "level": "INFO"}])
    loguru.logger.add("skyhouse.log", enqueue=True, level="DEBUG")
