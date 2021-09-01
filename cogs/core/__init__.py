import threading
import time

from loguru import logger

import runtimeConfig
from .svc import _redis, mongodb
from .auction_mainloop import fetch_all_auctions
from .profit import find_flips_in_thread


def fetch_mainloop():
    while True:
        logger.debug("fetching auctions")
        start = time.time()
        data = fetch_all_auctions()
        end = time.time()
        auctions = data["data"]
        logger.info(f"fetched and processed {len(auctions)} auctions in {round(end - start)} seconds")
        find_flips_in_thread()
        last_updated = data["last_updated"] / 1000
        next_update = last_updated + 60
        delta = next_update - time.time()
        if delta > 0:
            logger.debug(f"waiting {round(delta)} seconds for api update")
            time.sleep(delta + 0.1)


def setup():
    redis, pubsub = _redis.setup()  # noqa
    runtimeConfig.redis = redis
    runtimeConfig.pubsub = pubsub
    logger.info("Redis connection established")

    mongodb.setup()
    logger.info("MongoDB connection established")

    fetch_thread: threading.Thread = threading.Thread(target=fetch_mainloop)
    fetch_thread.setDaemon(True)
    fetch_thread.start()
