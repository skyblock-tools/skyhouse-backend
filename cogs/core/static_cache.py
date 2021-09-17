import runtimeConfig
import requests
import json

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


def get_json_file_in_drive(*filename, json_suffix=True) -> JsonWrapper:
    key = f"drive:{'/'.join(filename)}"
    if key not in _cache:
        get_json_file_in_drive_ignore_cache(*filename, json_suffix=json_suffix)
    return _cache[key]


def get_json_file_in_drive_ignore_cache(*filename, json_suffix=True) -> JsonWrapper:
    key = f"drive:{'/'.join(filename)}"
    suffix = ".json" if json_suffix else ""
    with open(f"{'/'.join(filename)}{suffix}", "r") as f:
        _cache[key] = JsonWrapper.from_dict(json.loads(f.read()))
    return _cache[key]
