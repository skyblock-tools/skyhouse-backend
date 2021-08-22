import multiprocessing.pool
import time

import ujson
import concurrent.futures
import requests
from loguru import logger

import runtimeConfig
from utils import misc
from .auction import parse_auction, parse_ended_auction

auction_base_url = "https://api.hypixel.net/skyblock/auctions"
last_loop_run = 0


def process_auction(x):
    auction_obj = parse_auction(x)
    mapping = misc.redis_json_dump(auction_obj)
    return [auction_obj, mapping]


def process_ended_auction(x):
    return parse_ended_auction(x)


def fetch_all_auctions() -> dict:
    global last_loop_run
    pages = []

    def fetch_page(url=auction_base_url, page: int = None):
        nonlocal last_updated
        resp = requests.get(url, params={"page": page} if page else {})
        json = ujson.loads(resp.text)
        pages.append(json)
        if page != 0 and page == total_pages - 1:
            last_updated = json["lastUpdated"]
        return json

    last_updated = 0
    first_page = fetch_page(page=0)
    total_pages = first_page["totalPages"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as es:
        futures = (es.submit(fetch_page, page=page) for page in range(1, total_pages))
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
            except Exception as e:
                print(e)
    auctions = [item for page in pages for item in page["auctions"]]

    pipeline = runtimeConfig.redis.pipeline()
    pool = multiprocessing.pool.Pool(processes=10)

    existing = set(runtimeConfig.redis.keys("auction:*"))
    existing_bins = set(runtimeConfig.redis.keys("bin:*"))

    to_process = []
    for auction in auctions:
        if f"auction:{auction['uuid']}" in existing:
            if len(auction['bids']) > 0 and auction['bids'][-1]['timestamp'] > last_loop_run:
                to_process.append(auction)
        elif f'bin:{auction["uuid"]}' not in existing_bins:
            to_process.append(auction)

    logger.debug(f"processing, discarded {len(auctions) - len(to_process)} existing entries")
    processed = pool.map(process_auction, to_process)
    pool.close()

    total = len(processed)
    for i, chunk in enumerate(processed):
        data, mapping = chunk
        if data.end < time.time():
            delete_auction(pipeline, data, "uuid")
        _type = "bin" if data.bin else "auction"
        pipeline.hset(f"{_type}:{mapping['uuid']}", mapping=mapping)
        pipeline.zadd(f"{_type}s:{data.internal_name}", mapping={mapping["uuid"]: f'{mapping["price"]}'})

    logger.debug(f"inserting {total} auctions")
    pipeline.execute()

    ended = fetch_page("https://api.hypixel.net/skyblock/auctions_ended")["auctions"]

    pool = multiprocessing.pool.Pool(processes=10)

    logger.debug("processing ended auctions")
    processed = pool.map(process_ended_auction, ended)
    pool.close()

    total = len(processed)
    for i, data in enumerate(processed):
        delete_auction(pipeline, data)

    logger.debug(f"removing {total} ended auctions")
    pipeline.execute()

    last_loop_run = time.time()
    return {
        "data": auctions,
        "last_updated": last_updated,
    }


def delete_auction(redis_or_pipeline, data, uuid="auction_id"):
    _type = "bin" if data.bin else "auction"
    redis_or_pipeline.delete(f"{_type}:{data[uuid]}", f"{_type}flip:{data[uuid]}")
    redis_or_pipeline.zrem(f"bins:{data.internal_name}", data[uuid])
