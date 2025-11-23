import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://qa-internship.avito.com"
USERID = int(os.getenv("USERID"))

def make_request(method, endpoint, **kwargs):
    try:
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']
        response = requests.request(method=method.upper(), url=url, headers=headers, **kwargs)
        response.raise_for_status()
        if response.status_code == 200 and response.content:
            return response.json()
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка: {method} {endpoint}: {e}")
        return None

def create_item(name, price, statistics):
    seller_id = USERID
    payload = {
        "sellerID": seller_id,
        "name": name,
        "price": price,
        "statistics": statistics,
    }
    result = make_request("POST", "/api/1/item", json=payload)
    if result and 'status' in result:
        status_message = result['status']
        if 'Сохранили объявление - ' in status_message:
            item_id = status_message.replace('Сохранили объявление - ', '')
            return {"id": item_id}
    return result

def get_item(item_id):
    return make_request("GET", f"/api/1/item/{item_id}")

def delete_item(item_id):
    headers = {"Accept": "application/json"}
    result = make_request("DELETE", f"/api/2/item/{item_id}", headers=headers)
    return result is not None

def get_item_statistic(item_id):
    return make_request("GET", f"/api/1/statistic/{item_id}")

def get_item_statistic_v2(item_id):
    return make_request("GET", f"/api/2/statistic/{item_id}")

def create_statistics(likes=0, view_count=0, contacts=0):
    return {"likes": likes, "viewCount": view_count, "contacts": contacts}

def print_item_info(item):
    if item:
        print(f"ID: {item.get('id')}")
        print(f"Название: {item.get('name')}")
        print(f"Цена: {item.get('price')}")
        print(f"Продавец: {item.get('sellerId')}")
        print(f"Создано: {item.get('createdAt')}")
        stats = item.get("statistics")
        if stats:
            print(f"Лайки: {stats.get('likes')}")
            print(f"Просмотры: {stats.get('viewCount')}")
            print(f"Контакты: {stats.get('contacts')}")
        print("-" * 30)

if __name__ == "__main__":
    new_item = create_item(
        name="Тестовый товар",
        price=9900,
        statistics=create_statistics(likes=21, view_count=11, contacts=43)
    )
    
    if new_item and 'id' in new_item:
        item_id = new_item['id']
        item_data = get_item(item_id)
        if item_data and len(item_data) > 0:
            print_item_info(item_data[0])
            stats = get_item_statistic(item_id)
            print("Статистика v1:", stats)
            stats_v2 = get_item_statistic_v2(item_id)
            print("Статистика v2:", stats_v2)
            delete_item(item_id)