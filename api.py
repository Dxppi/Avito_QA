import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://qa-internship.avito.com"
USERID = int(os.getenv("USERID"))


def make_request(method: str, endpoint: str, **kwargs) -> requests.Response:
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    return requests.request(method=method.upper(), url=url, headers=headers, **kwargs)


def create_item(name: str, price: int, statistics: dict) -> dict:
    payload = {
        "sellerID": USERID,
        "name": name,
        "price": price,
        "statistics": statistics,
    }
    response = make_request("POST", "/api/1/item", json=payload)
    if response.status_code == 200:
        result = response.json()
        if "status" in result and "Сохранили объявление - " in result["status"]:
            item_id = result["status"].replace("Сохранили объявление - ", "") # Тут скорее всего бага, не должно с апи приходить json с "Сохранили в объявление -"
            return {"id": item_id}
    return None


def get_item(item_id: str) -> requests.Response:
    return make_request("GET", f"/api/1/item/{item_id}")


def get_all_items() -> requests.Response:
    return make_request("GET", f"/api/1/{USERID}/item")


def delete_item(item_id: str) -> bool:
    return make_request("DELETE", f"/api/2/item/{item_id}").status_code == 200


def get_item_statistic(item_id: str) -> requests.Response:
    return make_request("GET", f"/api/1/statistic/{item_id}")


def get_item_statistic_v2(item_id: str) -> requests.Response:
    return make_request("GET", f"/api/2/statistic/{item_id}")
