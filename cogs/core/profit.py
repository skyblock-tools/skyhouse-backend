import runtimeConfig


def find_bin_flips():
    items = runtimeConfig.redis.keys("bins:*")
    for item in items:
        l_bins = runtimeConfig.redis.zrange(item, 0, 5, withscores=True)
        if len(l_bins) != 5:
            continue
        profit = l_bins[1][1] - l_bins[0][1]
        print(f"{profit} profit on {item}")
