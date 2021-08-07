import runtimeConfig
from utils.JsonWrapper import JsonWrapper

webhook_url = ""


def flip_cb(message: dict):
    auc_id, profit = message['data'].split(':')
    info = JsonWrapper.from_dict(runtimeConfig.redis.hgetall(f"auction:{auc_id}"))
    output = f"""
    Name: {info.item_name}
    Price: {int(info.starting_bid):,}
    Profit: {int(profit):,}
    Command: `/viewauction {info.uuid}
    """
    # requests.post(webhook_url, data=ujson.dumps({
    #     "content": output
    # }), headers={"Content-Type": "application/json"})


# noinspection SpellCheckingInspection
def setup():
    pubsub = runtimeConfig.redis.pubsub()
    pubsub.subscribe(**{"binflip:profit": flip_cb})
    pubsub.run_in_thread()
    print("discord bot set up")
