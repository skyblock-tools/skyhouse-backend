import runtimeConfig


def find_flips():
    items = runtimeConfig.redis.keys("bins:*")
    pipeline = runtimeConfig.redis.pipeline()
    for item in items:
        l_bins = runtimeConfig.redis.zrange(item, 0, -1, withscores=True)
        flip = False
        if len(l_bins) >= 5:

            auctions = runtimeConfig.redis.zrange(f"auctions:{item[5:]}", 0, 5, withscores=True)
            for auction in auctions:
                profit = l_bins[0][1] - auction[1]
                profit -= l_bins[0][1] * 0.02  # remove the 2% selling tax from profit
                if profit > 100_000:
                    runtimeConfig.redis.publish("auctionflip:profit", f"{item[5:]}:{auction[0]}:{round(profit)}")
                    pipeline.hset(f"auctionflip:{item[9:]}", mapping={
                        "uuid": auction[0],
                        "profit": round(profit),
                        "resell_price": round(l_bins[0][1]),
                        "quantity": len(l_bins),
                        "type": "auction",
                    })
                    flip = True

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
                continue
        if not flip:
            pipeline.delete(f"*flip:{item[5:]}")
    pipeline.execute()



