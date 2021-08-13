import runtimeConfig
from utils.JsonWrapper import JsonWrapper
import discord_webhook

webhook_url = ""
webhook = discord_webhook.DiscordWebhook(url=webhook_url)


def bin_flip_cb(message: dict):
    auc_id, profit = message['data'].split(':')
    info = JsonWrapper.from_dict(runtimeConfig.redis.hgetall(f"bin:{auc_id}"))

    embed = discord_webhook.DiscordEmbed(title="AUCTION ALERT", color=0xCBCDCD, description="TYPE: BIN->BIN")
    embed.add_embed_field(name="» Profit", value=f"`{int(profit):,}", inline=False)
    embed.add_embed_field(name="» Price", value=f"`{int(info.price):,}`", inline=False)
    embed.add_embed_field(name="» Item", value=f"`{info.item_name}`", inline=False)
    embed.add_embed_field(name="» Rarity", value=f"`{info.tier}`", inline=False)
    embed.add_embed_field(name="» Seller", value=f"```\n/viewauction {info.uuid}\n```", inline=False)

    webhook.add_embed(embed)
    webhook.execute(remove_embeds=True)


# noinspection SpellCheckingInspection
def setup():
    pubsub = runtimeConfig.redis.pubsub()
    pubsub.subscribe(**{"binflip:profit": bin_flip_cb})
    pubsub.run_in_thread()
