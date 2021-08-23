import multiprocessing.pool
import time

import ujson
import concurrent.futures
import requests
from loguru import logger

import runtimeConfig
from utils import misc
from utils.JsonWrapper import JsonWrapper
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
        if page is not None:
            pages.append(json)
        if page != 0 and page is not None and page == total_pages - 1:
            last_updated = json["lastUpdated"]
        return json

    pipeline = runtimeConfig.redis.pipeline()

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

    existing_auctions = set(runtimeConfig.redis.keys("auction:*"))
    existing_bins = set(runtimeConfig.redis.keys("bin:*"))

    existing_auction_uuids = set([z.split(':')[2] for z in existing_auctions])
    existing_bin_uuids = set([z.split(':')[2] for z in existing_bins])
    existing_uuids = existing_auction_uuids.union(existing_bin_uuids)

    to_process = []
    for auction in auctions:
        if auction['uuid'] in existing_auction_uuids:
            if len(auction['bids']) > 0 and auction['bids'][-1]['timestamp'] > last_loop_run:
                to_process.append(auction)
        elif auction["uuid"] not in existing_bin_uuids:
            to_process.append(auction)

    logger.debug(f"processing, discarded {len(auctions) - len(to_process)} existing entries")
    processed = pool.map(process_auction, to_process)
    pool.close()

    total = len(processed)
    delete_pipeline = runtimeConfig.redis.pipeline()
    for i, chunk in enumerate(processed):
        data, mapping = chunk
        if data.end < time.time() * 1000 or data["uuid"] in existing_uuids:
            delete_auction(delete_pipeline, data, "uuid")
        _type = "bin" if data.bin else "auction"
        pipeline.hset(f"{_type}:{data.internal_name}:{mapping['uuid']}", mapping=mapping)
        pipeline.zadd(f"{_type}s:{data.internal_name}", mapping={mapping["uuid"]: f'{mapping["price"]}'})

    delete_pipeline.execute()

    logger.debug("culling removed auctions")

    uuids = set([z["uuid"] for z in auctions])
    to_remove = []

    for (_list, is_bin) in ((existing_auctions, False), (existing_bins, True)):
        for existing_auction in _list:
            _, i_name, uuid = existing_auction.split(':')
            if uuid not in uuids:
                to_remove.append(JsonWrapper.from_dict({
                    "auction_id": uuid,
                    "bin": is_bin,
                    "internal_name": i_name,
                }))

    for item in to_remove:
        delete_auction(delete_pipeline, item)
    delete_pipeline.execute()

    logger.debug(f"inserting {total} auctions")
    pipeline.execute()

    last_loop_run = time.time()
    return {
        "data": auctions,
        "last_updated": last_updated,
    }


def delete_auction(redis_or_pipeline, data, uuid="auction_id"):
    _type = "bin" if data.bin else "auction"
    redis_or_pipeline.delete(f"{_type}:{data.internal_name}:{data[uuid]}", f"{_type}flip:{data[uuid]}")
    redis_or_pipeline.zrem(f"bins:{data.internal_name}", data[uuid])
