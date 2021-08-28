import math
import re
import time

from utils.JsonWrapper import JsonWrapper
from utils import constants

TYPE_BIN = 1
TYPE_AUCTION = 2
TYPE_BIN_AUCTION = 3

SORT_PROFIT = 1
SORT_PROFIT_PROPORTION = 2
SORT_PRICE = 3
SORT_QUANTITY = 4

item_filters = [
    lambda auction: not auction.skin,  # remove skins
    lambda auction: not auction.pet,  # remove pets
    lambda auction: not auction.recomb,  # remove recombs
    lambda auction: not auction.soul,  # remove cake souls
    lambda auction: not auction.internal_name.startswith("ENCHANTED_BOOK"),  # remove enchanted books
]

no_priv_allowed_filters = [
    "limit",
    "min_quantity",
    "serve_nbt",
    "type",
]

default_filter = {
    "max_price": math.inf,
    "min_profit": 0,
    "bin_max_profit": math.inf,
    "min_time": -1,
    "max_time": math.inf,
    "min_tier": "common",
    "max_tier": "special",
    "regex": "",
    "sort": 1,
    "serve_nbt": False,
    "limit": 100,
    "min_quantity": 5,
    "max_quantity": math.inf,
    "item_filter": 0,
    "type": TYPE_BIN_AUCTION,
}


def parse_item_filter(_filter: int):
    output = []
    for i, func in enumerate(item_filters):
        if (2 ** i) & _filter != 0:
            output.append(func)
    return output


def parse_filter(json: dict, priv=True, level=1) -> JsonWrapper:
    output = {}
    for key in default_filter:
        if priv or key in no_priv_allowed_filters:
            if key in json:
                try:
                    output[key] = type(default_filter[key])(json[key])
                except (TypeError, ValueError):
                    output[key] = default_filter[key]
            else:
                output[key] = default_filter[key]
        else:
            output[key] = default_filter[key]
    output["item_filter"] = parse_item_filter(output["item_filter"]) if priv else []
    if level != 10:
        output['limit'] = min(output['limit'], 200 if priv else 100)
    return JsonWrapper.from_dict(output)


def include(auction, _filter):
    price_range = True
    if _filter.max_price != -1:
        price_range = int(auction.price) < _filter.max_price
    profit = int(auction.profit) >= _filter.min_profit and (
            (not bool(auction.bin)) or int(auction.profit) <= _filter.bin_max_profit)
    time_ = _filter.min_time < auction.end - time.time() <= _filter.max_time
    name = _filter.regex == "" or re.search(_filter.regex, auction.item_name)
    item_filter = all(map(lambda x: x(auction), _filter.item_filter))

    quantity = _filter.min_quantity <= int(auction.quantity) <= _filter.max_quantity

    type_ = _filter["type"] in [TYPE_BIN, TYPE_BIN_AUCTION] and auction.bin or _filter[
        "type"] in [TYPE_AUCTION, TYPE_BIN_AUCTION] and not auction.bin

    tier = False
    inside_tiers = False
    for _tier in constants.Skyblock.TIERS:
        if _tier.casefold() == _filter.min_tier.casefold():
            inside_tiers = True
        if _tier.casefold() == auction.tier.casefold() and inside_tiers:
            tier = True
        if _tier.casefold() == _filter.max_tier.casefold():
            break

    not_static_blacklist = auction.carpentry == "false" and ((not auction.internal_name.startswith("ENCHANTED_BOOK")) or
                                                             len(auction.internal_name.split(';')) < 2)

    return price_range and profit and time_ and name and item_filter and quantity and type_ and tier and not_static_blacklist
