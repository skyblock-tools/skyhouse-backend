import math
import threading
from loguru import logger
import time

import runtimeConfig

running = False


def find_flips_in_thread():
    if running:
        return
    thread: threading.Thread = threading.Thread(target=find_flips)
    thread.setDaemon(True)
    thread.start()


def find_flips():
    global running
    running = True
    start = time.time()
    logger.debug("Finding potential flips")

    items = runtimeConfig.redis.keys("bins:*")
    pipeline = runtimeConfig.redis.pipeline()

    for item in items:
        pipeline.zrangebyscore(item, 0, math.inf, withscores=True)
        pipeline.zrangebyscore(f"auctions:{item[5:]}", 0, math.inf, start=0, num=5, withscores=True)
    result = pipeline.execute()
    result = [(items[i // 2][5:], z, result[i + 1]) for i, z in [*enumerate(result)][::2]]

    for i_name, l_bins, auctions in result:
        find_flip_for_item_callback(pipeline, i_name, l_bins, auctions)

    pipeline.execute()
    running = False
    logger.info(f"Scanned {len(items)} item types for flips in {round(time.time() - start)} seconds")


def find_flip_for_item_callback(pipeline, i_name, l_bins, auctions):
    if len(l_bins) >= 5:
        auc_flip = False
        for auction in auctions:
            profit = l_bins[0][1] - auction[1]
            profit -= l_bins[0][1] * 0.02  # remove the 2% selling tax from profit
            if profit > 100_000:
                runtimeConfig.redis.publish("auctionflip:profit", f"{i_name}:{auction[0]}:{round(profit)}")
                pipeline.hset(f"auctionflip:{i_name}", mapping={
                    "uuid": auction[0],
                    "profit": round(profit),
                    "resell_price": round(l_bins[0][1]),
                    "quantity": len(l_bins),
                    "type": "auction",
                })
                auc_flip = True
        if not auc_flip:
            pipeline.delete(f"auctionflip:{i_name}")

        profit = l_bins[1][1] - l_bins[0][1]
        profit -= l_bins[1][1] * 0.02
        if profit > 100_000:
            pipeline.publish("binflip:profit", f"{i_name}:{l_bins[0][0]}:{round(profit)}")
            pipeline.hset(f"binflip:{i_name}", mapping={
                "uuid": l_bins[0][0],
                "profit": round(profit),
                "resell_price": round(l_bins[1][1]),
                "quantity": len(l_bins),
                "type": "bin",
            })
        else:
            pipeline.delete(f"binflip:{i_name}")
