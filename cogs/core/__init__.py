import threading
import time

from .redis import setup as redis_setup
from .auction_mainloop import fetch_all_auctions
import redis as _redis

redis: _redis.Redis or None = None
# noinspection SpellCheckingInspection
pubsub: _redis.client.PubSub or None = None


def mainloop():
    while True:
        print("fetching auctions...")
        start = time.time()
        data = fetch_all_auctions()
        end = time.time()
        auctions = data["data"]
        print(f"fetched {len(auctions)} auctions in {round(end - start)} seconds, waiting")

        last_updated = data["last_updated"] / 1000
        next_update = last_updated + 60
        delta = next_update - time.time()
        if delta > 0:
            print(f"waiting {round(delta)} seconds for api update")
            time.sleep(delta)


def setup():
    global redis, pubsub  # noqa
    redis, pubsub = redis_setup()  # noqa
    thread: threading.Thread = threading.Thread(target=mainloop)
    thread.setDaemon(True)
    thread.start()
