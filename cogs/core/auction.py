import gzip
import nbtlib
import io
import base64
import ujson

from utils.JsonWrapper import JsonWrapper


def get_internal_name_from_nbt(nbt):
    internal_name = ""
    nbt = nbt["tag"]
    if nbt is not None and "ExtraAttributes" in nbt:
        ea = nbt["ExtraAttributes"]
        if "id" in ea:
            internal_name = f"{ea['id']}".replace(":", "-")
        else:
            return None
        if internal_name == "PET":
            if "petInfo" not in ea:
                return None
            pet_info = ujson.loads(ea["petInfo"])
            internal_name = pet_info["type"]
            tier = pet_info["tier"]
            tiers = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY", "MYTHIC", "SPECIAL"]
            internal_name += f";{tiers.index(tier)}"
        elif internal_name == "ENCHANTED_BOOK":
            enchants = []
            try:
                enchants = ea["enchantments"]
            except KeyError:
                return None
            for enchant_name in enchants:
                internal_name += f"{enchant_name.upper()};{enchants[enchant_name]}"
    return internal_name


def decode_nbt(item_bytes: str) -> dict:
    return \
        nbtlib.File.from_fileobj(gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(item_bytes)))).unpack(json=True)[''][
            "i"][0]


def parse_auction(auction: dict) -> JsonWrapper:
    _nbt = decode_nbt(auction["item_bytes"])
    return JsonWrapper.from_dict({
        "nbt": _nbt,
        "internal_name": get_internal_name_from_nbt(_nbt),
    })
