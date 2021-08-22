import math
import re

from utils.JsonWrapper import JsonWrapper
from utils import constants

item_filters = [
    lambda auction: auction.skin == "false",  # remove skins
    lambda auction: auction.soul == "false",  # remove cake souls
    lambda auction: auction.pet == "false",  # remove pets
    lambda auction: auction.recomb == "false",  # remove recombs
]

no_priv_allowed_filters = [
    "limit",
    "serve_nbt",
]

default_filter = {
    "max_price": math.inf,
    "min_profit": 0,
    "bin_max_profit": math.inf,
    "min_time": -1,
    "max_time": math.inf,
    "min_tier": "common",
    "max_tier": "special",
    "regex": None,
    "sort": 1,
    "serve_nbt": False,
    "limit": 100,
    "min_quantity": 0,
    "max_quantity": math.inf,
    "item_filter": 0,
}


def parse_item_filter(_filter: int):
    output = []
    for i, func in enumerate(item_filters):
        if (2 ** i) & _filter != 0:
            output.append(func)
    return output


def parse_filter(json: dict, priv=True) -> JsonWrapper:
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
    output['limit'] = min(output['limit'], 200 if priv else 100)
    return JsonWrapper.from_dict(output)


def include(auction, _filter):
    price_range = True
    if _filter.max_price != -1:
        price_range = int(auction.price) < _filter.max_price
    profit = int(auction.profit) >= _filter.min_profit and (
            (not bool(auction.bin)) or int(auction.profit) <= _filter.bin_max_profit)
    time = _filter.min_time < auction.end <= _filter.max_time
    name = _filter.regex is None or re.search(_filter.regex, auction.item_name)
    item_filter = all(map(lambda x: x(auction), _filter.item_filter))

    tier = False
    inside_tiers = False
    for _tier in constants.Skyblock.TIERS:
        if _tier.casefold() == _filter.min_tier.casefold():
            inside_tiers = True
        if _tier.casefold() == auction.tier.casefold() and inside_tiers:
            tier = True
        if _tier.casefold() == _filter.max_tier.casefold():
            break

    return price_range and profit and time and name and item_filter and tier
