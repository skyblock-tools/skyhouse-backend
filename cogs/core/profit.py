import math
import threading

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
    items = runtimeConfig.redis.keys("bins:*")
    pipeline = runtimeConfig.redis.pipeline()
    for item in items:
        l_bins = runtimeConfig.redis.zrangebyscore(item, 0, math.inf, withscores=True)
        if len(l_bins) >= 5:
            auctions = runtimeConfig.redis.zrangebyscore(f"auctions:{item[5:]}", 0, math.inf, start=0, num=5,
                                                         withscores=True)
            auc_flip = False
            for auction in auctions:
                profit = l_bins[0][1] - auction[1]
                profit -= l_bins[0][1] * 0.02  # remove the 2% selling tax from profit
                if profit > 100_000:
                    runtimeConfig.redis.publish("auctionflip:profit", f"{item[5:]}:{auction[0]}:{round(profit)}")
                    pipeline.hset(f"auctionflip:{item[5:]}", mapping={
                        "uuid": auction[0],
                        "profit": round(profit),
                        "resell_price": round(l_bins[0][1]),
                        "quantity": len(l_bins),
                        "type": "auction",
                    })
                    auc_flip = True
            if not auc_flip:
                pipeline.delete(f"auctionflip:{item[5:]}")

            profit = l_bins[1][1] - l_bins[0][1]
            profit -= l_bins[1][1] * 0.02
            if profit > 100_000:
                pipeline.publish("binflip:profit", f"{item[5:]}:{l_bins[0][0]}:{round(profit)}")
                pipeline.hset(f"binflip:{item[5:]}", mapping={
                    "uuid": l_bins[0][0],
                    "profit": round(profit),
                    "resell_price": round(l_bins[1][1]),
                    "quantity": len(l_bins),
                    "type": "bin",
                })
            else:
                pipeline.delete(f"binflip:{item[5:]}")
    pipeline.execute()
    running = False
