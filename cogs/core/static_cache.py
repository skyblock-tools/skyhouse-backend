import runtimeConfig
import requests

from utils.JsonWrapper import JsonWrapper

_cache = {}


def get_json_file(*filename, base: str = runtimeConfig.static_base_url, json_suffix=True) -> JsonWrapper:
    key = f"{base}:{'/'.join(filename)}"
    if key not in _cache:
        get_json_file_ignore_cache(*filename, base=base, json_suffix=json_suffix)
    return _cache[key]


def get_json_file_ignore_cache(*filename, base: str = runtimeConfig.static_base_url, json_suffix=True) -> JsonWrapper:
    key = f"{base}:{'/'.join(filename)}"
    suffix = ".json" if json_suffix else ""
    _cache[key] = JsonWrapper.from_dict(requests.get(f"{base}/{'/'.join(filename)}{suffix}").json())
    return _cache[key]
