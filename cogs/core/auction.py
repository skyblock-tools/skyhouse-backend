import gzip
import re

import nbtlib
import io
import base64
import json

from utils import constants, skyblock
from utils.JsonWrapper import JsonWrapper
from . import static_cache


def get_internal_name_from_nbt(nbt):
    internal_name = ""
    nbt = nbt["tag"]
    if nbt is not None and "ExtraAttributes" in nbt:
        ea = nbt["ExtraAttributes"]
        enchants = ea.get("enchantments", {})
        if "id" in ea:
            internal_name = f"{ea['id']}".replace(":", "-")
        else:
            return None
        if internal_name == "PET":
            if "petInfo" not in ea:
                return None
            pet_info = json.loads(ea["petInfo"])
            internal_name = pet_info["type"]
            tier = pet_info["tier"]
            tiers = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY", "MYTHIC", "SPECIAL"]

            pet_level_group = skyblock.get_level_from_table(constants.Misc.PET_LEVEL_GROUPS,
                                                            skyblock.get_level_from_pet_xp(tier, pet_info["exp"]))
            internal_name += f";{tiers.index(tier)};{pet_level_group}"
        elif internal_name == "ENCHANTED_BOOK":
            if not enchants:
                return None
            for enchant_name in enchants:
                internal_name += f";{enchant_name.upper()}-{enchants[enchant_name]}"
        elif enchants:
            ec_levels = static_cache.get_json_file("prices", "enchant_levels")
            ecs = {}
            for enchant_name in enchants:
                for i, level in enumerate(ec_levels.levels):
                    if enchant_name.upper() in level:
                        ecs[i] = max(enchants[enchant_name], ecs.get(i, 0))
                if enchant_name in ec_levels.keep:
                    internal_name += f";{enchant_name}-{enchants[enchant_name]}"
            if ecs:
                internal_name += f";{max(ecs.keys())}-{ecs[max(ecs.keys())]}"
    return internal_name


def get_item_head_url_from_nbt(nbt):
    try:
        if "SkullOwner" in nbt["tag"]:
            return "https://mc-heads.net/head/" + \
                   json.loads(base64.b64decode(nbt["tag"]["SkullOwner"]["Properties"]["textures"][0]["Value"]))[
                       "textures"][
                       "SKIN"]['url'].split("/")[4]
        else:
            return None
    except (KeyError, Exception):
        return None


def get_display_name_from_nbt(nbt):
    try:
        return nbt["tag"]["display"]["Name"]
    except KeyError:
        return None


def get_bare_skyblock_id_from_nbt(nbt):
    try:
        return nbt["tag"]["ExtraAttributes"]["id"]
    except KeyError:
        return None


def decode_nbt(item_bytes: str) -> dict:
    return \
        nbtlib.File.from_fileobj(gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(item_bytes)))).unpack(json=True)[''][
            "i"][0]


auction_attrs = [
    "item_name",
    "item_bytes",
    "tier",
    "uuid",
]


def parse_ended_auction(auction: dict) -> JsonWrapper:
    _nbt = decode_nbt(auction["item_bytes"])
    return JsonWrapper.from_dict({
        **auction,
        "nbt": _nbt,
        "internal_name": get_internal_name_from_nbt(_nbt),
        "bin": auction.get("bin", False),
    })


def parse_auction(auction: dict) -> JsonWrapper:
    _nbt = decode_nbt(auction["item_bytes"])
    output = JsonWrapper.from_dict({
        "nbt": _nbt,
        "internal_name": get_internal_name_from_nbt(_nbt),
        "lore": auction["item_lore"],
        "display_name": get_display_name_from_nbt(_nbt),
        "skyblock_id": get_bare_skyblock_id_from_nbt(_nbt),
        "head_url": get_item_head_url_from_nbt(_nbt) if "SkullOwner" in _nbt["tag"] else "",
    })
    for attr in auction_attrs:
        output[attr] = auction.get(attr, None)
    output.tier = output.tier.upper()
    output.pet = "[Lvl" in output.item_name
    output.candy = -1
    if output.pet:
        output.candy = int(re.search(r"(\d+)/(\d+)\) Pet Candy Used", auction["item_lore"]).group(1)) \
            if " Pet Candy Used" in auction["item_lore"] else 0
        if "Tier Boost" in auction["item_lore"]:
            output.tier = constants.Skyblock.TIERS[constants.Skyblock.TIERS.index(output.tier.lower()) + 1]

    output.bin = "bin" in auction and auction["bin"]
    output.recomb = "§k" in auction["item_lore"]
    if output.recomb:
        output.tier = constants.Skyblock.TIERS[constants.Skyblock.TIERS.index(output.tier.lower()) - 1].upper()
    output.carpentry = "Furniture" in auction["item_lore"]
    output.skin = "Skin" in output.item_name
    output.soul = "Cake Soul" in auction["item_lore"]
    output.price = auction["highest_bid_amount"] if not output.bin and auction["highest_bid_amount"] != 0 \
        else auction["starting_bid"]
    output.end = round(auction["end"] / 1000)

    return output


display_props = [
    "profit",
    "resell_price",
    "quantity",
    "type",
    "item_bytes",
    "uuid",
    "item_name",
    "price",
    "end",
    "lore",
    "tier",
    "display_name",
    "skyblock_id",
    "head_url",
    "recomb",  # noqa
    "soul",
    "skin",
    "pet",
]


def get_api_output(auction: dict):
    output = {}
    for key in display_props:
        if key in auction:
            output[key] = auction[key]
    output["end"] = int(output["end"]) * 1000
    return output
