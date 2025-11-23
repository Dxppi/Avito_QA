import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://qa-internship.avito.com"
USERID = int(os.getenv("USERID"))


def make_request(method, endpoint, **kwargs):
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if "headers" in kwargs:
        headers.update(kwargs["headers"])
        del kwargs["headers"]

    response = requests.request(
        method=method.upper(), url=url, headers=headers, **kwargs
    )
    return response


def create_item(name, price, statistics):
    seller_id = USERID
    payload = {
        "sellerID": seller_id,
        "name": name,
        "price": price,
        "statistics": statistics,
    }
    response = make_request("POST", "/api/1/item", json=payload)
    if response.status_code == 200:
        result = response.json()
        if "status" in result:
            status_message = result["status"]
            if "Сохранили объявление - " in status_message:
                item_id = status_message.replace("Сохранили объявление - ", "")
                return {"id": item_id}
    return None


def get_item(item_id):
    return make_request("GET", f"/api/1/item/{item_id}")


def delete_item(item_id):
    headers = {"Accept": "application/json"}
    response = make_request("DELETE", f"/api/2/item/{item_id}", headers=headers)
    return response.status_code == 200


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
    print("Тестирование API...")
    
    # Создание объявления
    print("1. Создание объявления:")
    new_item = create_item(
        "Тестовый товар", 
        9900, 
        {"likes": 21, "viewCount": 11, "contacts": 43}
    )
    
    if new_item and "id" in new_item:
        item_id = new_item["id"]
        print(f"✓ Создано объявление с ID: {item_id}")
        
        # Получение объявления
        print("2. Получение объявления:")
        response = get_item(item_id)
        if response.status_code == 200:
            item_data = response.json()
            if item_data and len(item_data) > 0:
                print_item_info(item_data[0])
                print("✓ Объявление получено")
            else:
                print("✗ Не удалось получить данные объявления")
        else:
            print(f"✗ Ошибка получения: {response.status_code}")
        
        # Статистика
        print("3. Проверка статистики:")
        response = get_item_statistic(item_id)
        if response.status_code == 200:
            print("✓ Статистика v1 работает")
        else:
            print(f"✗ Статистика v1: {response.status_code}")
            
        response = get_item_statistic_v2(item_id)
        if response.status_code == 200:
            print("✓ Статистика v2 работает")
        else:
            print(f"✗ Статистика v2: {response.status_code}")
        
        # Удаление
        print("4. Удаление объявления:")
        if delete_item(item_id):
            print("✓ Удаление выполнено")
            
            # Проверка что удалилось
            response = get_item(item_id)
            if response.status_code == 404:
                print("✓ Объявление действительно удалено")
            else:
                print("✗ Объявление не удалено")
        else:
            print("✗ Ошибка удаления")
            
    else:
        print("✗ Не удалось создать объявление")
    
    print("Тестирование завершено!")