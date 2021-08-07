import multiprocessing.pool

import ujson
import concurrent.futures
import requests
import runtimeConfig
from .auction import parse_auction

auction_base_url = "https://api.hypixel.net/skyblock/auctions"


def process_auction(x):
    auction_obj = parse_auction(x)
    mapping = {k: v if type(v) in [str, int, float] else ujson.dumps(v) for k, v in x.items()}
    return [auction_obj, mapping]


def fetch_all_auctions() -> dict:
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

    to_process = []
    for auction in auctions:
        if f'auction:{auction["uuid"]}' not in existing:
            to_process.append(auction)

    print(f"processing, discarded {len(auctions) - len(to_process)} existing entries")
    processed = pool.map(process_auction, to_process)
    pool.close()

    print("postprocessing new auctions")

    total = len(processed)
    for i, chunk in enumerate(processed):
        data, mapping = chunk
        pipeline.hset(f"auction:{mapping['uuid']}", mapping=mapping)
        pipeline.zadd(f"bins:{data.internal_name}", mapping={mapping["uuid"]: mapping["starting_bid"]})

    print(f"inserting {total} auctions")
    pipeline.execute()

    print("fetching ended auctions")

    ended = fetch_page("https://api.hypixel.net/skyblock/auctions_ended")["auctions"]

    pool = multiprocessing.pool.Pool(processes=10)

    print("processing ended auctions")
    processed = pool.map(process_auction, ended)
    pool.close()

    total = len(processed)
    for i, chunk in enumerate(processed):
        data, mapping = chunk
        pipeline.delete(f"auction:{mapping['auction_id']}")
        pipeline.zrem(f"bins:{data.internal_name}", mapping['auction_id'])

    print(f"removing {total} ended auctions")
    pipeline.execute()

    return {
        "data": auctions,
        "last_updated": last_updated,
    }
