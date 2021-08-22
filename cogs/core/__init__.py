import threading
import time

from loguru import logger

import runtimeConfig
from .svc import _redis, mongodb
from .auction_mainloop import fetch_all_auctions
from .profit import find_flips


def mainloop():
    while True:
        logger.debug("fetching auctions")
        start = time.time()
        data = fetch_all_auctions()
        end = time.time()
        auctions = data["data"]
        logger.info(f"fetched and processed {len(auctions)} auctions in {round(end - start)} seconds")
        bin_flip_thread: threading.Thread = threading.Thread(target=find_flips)
        bin_flip_thread.setDaemon(True)
        bin_flip_thread.start()
        last_updated = data["last_updated"] / 1000
        next_update = last_updated + 60
        delta = next_update - time.time()
        if delta > 0:
            logger.debug(f"waiting {round(delta)} seconds for api update")
            time.sleep(delta)


def setup():
    redis, pubsub = _redis.setup()  # noqa
    runtimeConfig.redis = redis
    runtimeConfig.pubsub = pubsub
    logger.info("Redis connection established")

    mongodb.setup()
    logger.info("MongoDB connection established")

    thread: threading.Thread = threading.Thread(target=mainloop)
    thread.setDaemon(True)
    thread.start()
