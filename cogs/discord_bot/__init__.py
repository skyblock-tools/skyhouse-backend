import time

import runtimeConfig
from utils.JsonWrapper import JsonWrapper
import discord_webhook

webhooks = {}


def flip_cb(message: dict):
    auc_id, profit = message['data'].split(':')
    _type = message['channel'].split(':')[0][:-4]
    info = runtimeConfig.redis.hgetall(f"{_type}:{auc_id}")
    if not info:
        return
    info = JsonWrapper.from_dict(info)
    if _type == "auction" and int(info["end"]) / 1000 - time.time() > 300:
        return

    embed = discord_webhook.DiscordEmbed(title="AUCTION ALERT", color=0xCBCDCD,
                                         description=f"TYPE: {_type.upper()}->BIN")
    embed.add_embed_field(name="» Profit", value=f"`{int(profit):,}`", inline=False)
    embed.add_embed_field(name="» Price", value=f"`{int(info.price):,}`", inline=False)
    embed.add_embed_field(name="» Item", value=f"`{info.item_name}`", inline=False)
    embed.add_embed_field(name="» Rarity", value=f"`{info.tier}`", inline=False)
    embed.add_embed_field(name="» Seller", value=f"```\n/viewauction {info.uuid}\n```", inline=False)

    webhook = webhooks[_type]
    webhook.add_embed(embed)
    if len(webhook.embeds) == 10:
        webhook.execute(remove_embeds=True)


# noinspection SpellCheckingInspection
def setup():
    for webhook in runtimeConfig.webhooks:
        webhooks[webhook] = discord_webhook.DiscordWebhook(url=runtimeConfig.webhooks[webhook], rate_limit_retry=True)
    pubsub = runtimeConfig.redis.pubsub()
    pubsub.subscribe(**{"binflip:profit": flip_cb, "auctionflip:profit": flip_cb})
    pubsub.run_in_thread()
