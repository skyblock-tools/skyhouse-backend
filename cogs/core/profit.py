import runtimeConfig


def find_bin_flips():
    items = runtimeConfig.redis.keys("bins:*")
    for item in items:
        l_bins = runtimeConfig.redis.zrange(item, 0, 5, withscores=True)
        if len(l_bins) == 5:
            profit = l_bins[1][1] - l_bins[0][1]
            if profit > 100_000:
                runtimeConfig.redis.publish("binflip:profit", f"{l_bins[0][0]}:{round(profit)}")
                runtimeConfig.redis.hset(f"binflip:{item[5:]}", mapping={
                    "uuid": l_bins[0][0],
                    "profit": profit
                })
                continue
        runtimeConfig.redis.delete(f"flip:{item[5:]}")

