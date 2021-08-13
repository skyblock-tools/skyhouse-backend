import runtimeConfig


def find_bin_flips():
    items = runtimeConfig.redis.keys("bins:*")
    pipeline = runtimeConfig.redis.pipeline()
    for item in items:
        l_bins = runtimeConfig.redis.zrange(item, -1, -1, withscores=True)
        if len(l_bins) >= 5:
            profit = l_bins[1][1] - l_bins[0][1]
            if profit > 100_000:
                pipeline.publish("binflip:profit", f"{l_bins[0][0]}:{round(profit)}")
                pipeline.hset(f"binflip:{item[5:]}", mapping={
                    "uuid": l_bins[0][0],
                    "profit": profit,
                    "quantity": len(l_bins),
                })
                continue
        pipeline.delete(f"flip:{item[5:]}")
    pipeline.execute()

