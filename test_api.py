import pytest
from api import (
    USERID,
    make_request,
    create_item,
    get_item,
    get_all_items,
    delete_item,
    get_item_statistic,
    get_item_statistic_v2,
)


@pytest.fixture
def test_item():
    """Фикстура создает тестовое объявление и удаляет его после теста"""
    item = create_item("Test Item", 1000, {"likes": 1, "viewCount": 1, "contacts": 1})
    yield item
    if item and "id" in item:
        delete_item(item["id"])


def test_create_item_success(test_item):
    """TC-C-001: Успешное создание объявления с корректными данными"""
    assert test_item is not None
    assert "id" in test_item
    response = get_item(test_item["id"])
    assert response.status_code == 200
    item_data = response.json()
    assert len(item_data) > 0
    assert item_data[0]["name"] == "Test Item"
    assert item_data[0]["price"] == 1000


def test_create_item_missing_name():
    """TC-C-002: Создание без обязательного поля name"""
    payload = {
        "sellerID": USERID,
        "price": 1000,
        "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
    }
    response = make_request("POST", "/api/1/item", json=payload)
    assert response.status_code == 400


def test_create_item_empty_name():
    """TC-C-005: Создание с пустым названием"""
    item = create_item("", 1000, {"likes": 1, "viewCount": 1, "contacts": 1})
    assert item is None


def test_create_item_invalid_data():
    """TC-C-002: Создание с пустым телом запроса"""
    response = make_request("POST", "/api/1/item", json={})
    assert response.status_code == 400


def test_create_item_string_price():
    """TC-C-003: Создание с некорректным типом цены"""
    payload = {
        "sellerID": USERID,
        "name": "Test Item",
        "price": "not_a_number",
        "statistics": {"likes": 1, "viewCount": 1, "contacts": 1},
    }
    response = make_request("POST", "/api/1/item", json=payload)
    assert response.status_code == 400


def test_create_item_max_values():
    """TC-C-004: Создание с максимальными значениями"""
    payload = {
        "sellerID": USERID,
        "name": "Max Values Test",
        "price": 2147483647,
        "statistics": {
            "likes": 2147483647,
            "viewCount": 2147483647,
            "contacts": 2147483647,
        },
    }
    response = make_request("POST", "/api/1/item", json=payload)
    assert response.status_code in [200, 400]


def test_create_item_with_negative_values():
    """TC-C-006: Создание с отрицательными значениями"""
    item = create_item(
        "Negative Test", -100, {"likes": -10, "viewCount": -5, "contacts": -1}
    )
    assert item is not None
    response = get_item(item["id"])
    assert response.status_code == 200
    delete_item(item["id"])


def test_delete_item():
    """TC-G-003: Удаление объявления и проверка отсутствия"""
    item = create_item("Test Delete", 2000, {"likes": 2, "viewCount": 2, "contacts": 2})
    assert item is not None
    response = delete_item(item["id"])
    assert response
    response = get_item(item["id"])
    assert response.status_code == 404


def test_get_nonexistent_item():
    """TC-G-002: Получение несуществующего объявления"""
    response = get_item("Nonexistent_ID")
    assert response.status_code == 400


def test_get_all_user_items_with_created_items():
    """TC-A-001: Получение всех объявлений продавца с несколькими items"""
    created_items = []
    test_items_data = [
        ("Test Item One", 1000, {"likes": 1, "viewCount": 1, "contacts": 1}),
        ("Test Item Two", 2000, {"likes": 2, "viewCount": 2, "contacts": 2}),
        ("Test Item Three", 3000, {"likes": 3, "viewCount": 3, "contacts": 3}),
    ]
    for name, price, stats in test_items_data:
        item = create_item(name, price, stats)
        if item is not None:
            created_items.append(item)
    if len(created_items) > 0:
        response = get_all_items()
        assert response.status_code == 200
        all_items = response.json()
        assert isinstance(all_items, list)
        assert len(all_items) >= len(created_items)
        created_ids = {item["id"] for item in created_items}
        response_ids = {item["id"] for item in all_items}
        for created_id in created_ids:
            assert created_id in response_ids
    for item in created_items:
        delete_item(item["id"])


def test_get_all_items_empty_seller():
    """TC-A-002: Получение объявлений для продавца без объявлений"""
    unique_seller_id = 999999
    response = make_request("GET", f"/api/1/{unique_seller_id}/item")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)


def test_get_all_items_invalid_seller_id():
    """TC-A-003: Получение с невалидным sellerID"""
    response = make_request("GET", "/api/1/invalid_seller_id/item")
    assert response.status_code == 400


def test_statistics_endpoints(test_item):
    """TC-S-001/TC-S-003: Получение статистики через v1 и v2 эндпоинты"""
    response = get_item_statistic(test_item["id"])
    assert response.status_code == 200
    response = get_item_statistic_v2(test_item["id"])
    assert response.status_code == 200


def test_get_item_statistic_values_match():
    """TC-S-001: Проверка совпадения значений статистики"""
    item = create_item(
        "Stat Values Test", 1500, {"likes": 7, "viewCount": 12, "contacts": 3}
    )
    assert item is not None
    response = get_item_statistic(item["id"])
    assert response.status_code == 200
    stats_data = response.json()
    if stats_data and len(stats_data) > 0:
        stats = stats_data[0]
        assert stats["likes"] == 7
        assert stats["viewCount"] == 12
        assert stats["contacts"] == 3
    delete_item(item["id"])


def test_statistics_nonexistent_item():
    """TC-S-002/TC-S-004: Статистика несуществующего объявления"""
    response = get_item_statistic("665473")
    assert response.status_code == 400
    response = get_item_statistic_v2("665473")
    assert response.status_code == 404


def test_delete_nonexistent_item():
    """TC-D-002: Удаление несуществующего объявления"""
    response = make_request("DELETE", "/api/2/item/nonexistent-id-12345")
    assert response.status_code == 400


def test_delete_already_deleted_item():
    """TC-D-003: Повторное удаление уже удаленного объявления"""
    item = create_item(
        "Test Delete Twice", 1000, {"likes": 1, "viewCount": 1, "contacts": 1}
    )
    assert item is not None
    response1 = delete_item(item["id"])
    assert response1
    response2 = delete_item(item["id"])
    assert not response2


def test_compare_statistics_v1_v2():
    """TC-SV-001: Сравнение статистики v1 и v2"""
    item = create_item(
        "Compare Stats", 1000, {"likes": 5, "viewCount": 10, "contacts": 3}
    )
    assert item is not None
    response_v1 = get_item_statistic(item["id"])
    response_v2 = get_item_statistic_v2(item["id"])
    assert response_v1.status_code == 200
    assert response_v2.status_code == 200
    stats_v1 = response_v1.json()
    stats_v2 = response_v2.json()
    assert stats_v1 == stats_v2
    delete_item(item["id"])


def test_integration_full_lifecycle():
    """TC-I-001: Полный жизненный цикл объявления"""
    item = create_item(
        "Integration Test", 2500, {"likes": 8, "viewCount": 15, "contacts": 4}
    )
    assert item is not None
    item_id = item["id"]
    response_get = get_item(item_id)
    assert response_get.status_code == 200
    response_stats = get_item_statistic(item_id)
    assert response_stats.status_code == 200
    response_all = get_all_items()
    assert response_all.status_code == 200
    all_items = response_all.json()
    assert any(i["id"] == item_id for i in all_items)
    response_delete = delete_item(item_id)
    assert response_delete
    response_check = get_item(item_id)
    assert response_check.status_code == 404
