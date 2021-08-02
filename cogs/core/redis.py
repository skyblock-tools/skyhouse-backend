import redis as _redis
import runtimeConfig


def setup() -> [_redis.Redis, _redis.client.PubSub]:
    redis = _redis.Redis(**runtimeConfig.redis_options)

    # noinspection SpellCheckingInspection
    pubsub = redis.pubsub()
    # pubsub.run_in_thread(daemon=True)
    return [redis, pubsub]
