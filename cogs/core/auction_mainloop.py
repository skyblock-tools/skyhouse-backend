import orjson
import concurrent.futures
import requests

auction_base_url = "https://api.hypixel.net/skyblock/auctions"


def fetch_all_auctions() -> dict:
    pages = []

    def fetch_page(page: int):
        nonlocal last_updated
        resp = requests.get(auction_base_url, params={"page": page})
        json = orjson.loads(resp.text)
        pages.append(json)
        if page != 0 and page == total_pages - 1:
            last_updated = json["lastUpdated"]
        return json

    last_updated = 0
    first_page = fetch_page(0)
    total_pages = first_page["totalPages"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as es:
        futures = (es.submit(fetch_page, page) for page in range(1, total_pages))
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
            except Exception as e:
                print(e)
    return {
        "data": [item for page in pages for item in page["auctions"]],
        "last_updated": last_updated,
    }
