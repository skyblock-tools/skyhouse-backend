import random
import time

import runtimeConfig
from utils import auction_filter
from utils.JsonWrapper import JsonWrapper
import discord_webhook

webhooks = {}
default_filter = auction_filter.parse_filter({})

footers = [
    "Bot creators' server: https://discord.gg/kPGE84Gf67",
    "Check out our other project: https://skyblock.tools",
    "Skyhouse: https://discord.gg/kPGE84Gf67",
    "Get BIN->BIN flips as well: https://skyblock.tools",
    "Get flips right in your game: https://discord.gg/kPGE84Gf67",
    "More flips: https://skyblock.tools",
]


def flip_cb(message: dict):
    i_name, auc_id, profit = message['data'].split(':')
    _type = message['channel'].split(':')[0][:-4]
    info = runtimeConfig.redis.hgetall(f"{_type}:{i_name}:{auc_id}")
    if not info:
        return
    info = JsonWrapper.from_dict(info | {
        "profit": profit,
        "quantity": 10,
    })
    info.parse_str_ints()
    if (_type == "auction" and info["end"] - time.time() > 300) or not \
            auction_filter.include(info, default_filter):
        return

    embed = discord_webhook.DiscordEmbed(title="AUCTION ALERT", color=0xCBCDCD,
                                         description=f"TYPE: {_type.upper()}->BIN")
    embed.add_embed_field(name="» Profit", value=f"`{int(profit):,}`", inline=False)
    embed.add_embed_field(name="» Price", value=f"`{int(info.price):,}`", inline=False)
    embed.add_embed_field(name="» Item", value=f"`{info.item_name}`", inline=False)
    embed.add_embed_field(name="» Rarity", value=f"`{info.tier}`", inline=False)
    embed.add_embed_field(name="» Seller", value=f"```\n/viewauction {info.uuid}\n```", inline=False)
    embed.set_footer(text=random.choice(footers))

    for webhook in webhooks[_type]:
        webhook["webhook"].add_embed(embed)
        if len(webhook["webhook"].embeds) == 10 or (webhook["last"] != 0 and time.time() - webhook["last"] > 10):
            webhook["webhook"].execute(remove_embeds=True)
            webhook["last"] = 0
        else:
            webhook["last"] = time.time()


# noinspection SpellCheckingInspection
def setup():
    for webhook in runtimeConfig.webhooks:
        webhooks[webhook] = [{"last": 0, "webhook": discord_webhook.DiscordWebhook(url=link, rate_limit_retry=True)} for
                             link in
                             runtimeConfig.webhooks[webhook]]
    pubsub = runtimeConfig.redis.pubsub()
    pubsub.subscribe(**{"binflip:profit": flip_cb, "auctionflip:profit": flip_cb})
    pubsub.run_in_thread()
