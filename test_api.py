import pytest
from api import (
    make_request,
    create_item,
    get_item,
    delete_item,
    get_item_statistic,
    get_item_statistic_v2,
)


@pytest.fixture
def test_item():
    item = create_item("Test Item", 1000, {"likes": 1, "viewCount": 1, "contacts": 1})
    yield item
    if item and "id" in item:
        delete_item(item["id"])


def test_create_item_success(test_item):
    assert test_item is not None
    assert "id" in test_item
    response = get_item(test_item["id"])
    assert response.status_code == 200
    item_data = response.json()
    assert len(item_data) > 0
    assert item_data[0]["name"] == "Test Item"
    assert item_data[0]["price"] == 1000


def test_get_nonexistent_item():
    response = get_item("665473")
    assert response.status_code == 400


def test_delete_item():
    item = create_item("Test Delete", 2000, {"likes": 2, "viewCount": 2, "contacts": 2})
    assert item is not None
    response = delete_item(item["id"])
    assert response
    response = get_item(item["id"])
    assert response.status_code == 404


def test_statistics_endpoints(test_item):
    response = get_item_statistic(test_item["id"])
    assert response.status_code == 200
    response = get_item_statistic_v2(test_item["id"])
    assert response.status_code == 200


def test_create_item_invalid_data():
    response = make_request("POST", "/api/1/item", json={})
    assert response.status_code == 400


def test_statistics_nonexistent_item():
    response = get_item_statistic("665473")
    assert response.status_code == 400
    response = get_item_statistic_v2("665473")
    assert response.status_code == 404


def test_create_item_with_negative_values():
    item = create_item(
        "Negative Test", -100, {"likes": -10, "viewCount": -5, "contacts": -1}
    )
    assert item is not None
    response = get_item(item["id"])
    assert response.status_code == 200
    delete_item(item["id"])


def test_create_item_empty_name():
    item = create_item("", 1000, {"likes": 1, "viewCount": 1, "contacts": 1})
    assert item is None
