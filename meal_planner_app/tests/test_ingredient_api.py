"""API tests for master-ingredient catalog CRUD."""

import json
import uuid

from meal_planner_app.main import app
from meal_planner_app import crud


def _client():
    crud.reset_recipes_db()
    return app.test_client()


def _post_ingredient(client, payload):
    return client.post("/api/ingredients", json=payload)


def test_create_ingredient_success():
    client = _client()
    response = _post_ingredient(
        client,
        {
            "name": "  Flour  ",
            "default_unit": "cups",
            "location": "Baking",
            "location_id": "aisle-4",
        },
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["name"] == "Flour"
    assert data["default_unit"] == "cups"
    assert data["location"] == "Baking"
    assert data["location_id"] == "aisle-4"
    assert data["usage_count"] == 0
    uuid.UUID(data["id"])


def test_create_ingredient_missing_name_400():
    client = _client()
    assert _post_ingredient(client, {"default_unit": "g"}).status_code == 400
    assert _post_ingredient(client, {"name": "   "}).status_code == 400
    assert _post_ingredient(client, {}).status_code == 400


def test_create_ingredient_duplicate_name_409():
    client = _client()
    first = _post_ingredient(client, {"name": "Salt"})
    assert first.status_code == 201
    response = _post_ingredient(client, {"name": "  Salt  "})
    assert response.status_code == 409
    data = json.loads(response.data)
    assert "error" in data


def test_list_returns_ingredient_objects():
    client = _client()
    created = json.loads(_post_ingredient(client, {"name": "Pepper"}).data)
    response = client.get("/api/ingredients")
    assert response.status_code == 200
    items = json.loads(response.data)
    assert isinstance(items, list)
    pepper = next(item for item in items if item["name"] == "Pepper")
    assert pepper["id"] == created["id"]
    assert pepper["name"] == "Pepper"
    assert pepper["usage_count"] == 0
    assert "unit" in pepper
    assert "location" in pepper


def test_summary_includes_id():
    client = _client()
    created = json.loads(
        _post_ingredient(client, {"name": "Yeast", "default_unit": "g"}).data
    )
    response = client.get("/api/ingredients")
    assert response.status_code == 200
    summaries = json.loads(response.data)
    yeast = next(item for item in summaries if item["name"] == "Yeast")
    assert yeast["id"] == created["id"]
    assert yeast["unit"] == "g"
    assert yeast["usage_count"] == 0
    assert yeast["location"] == ""


def test_get_ingredient_by_id():
    client = _client()
    created = json.loads(
        _post_ingredient(client, {"name": "Butter", "location": "Dairy"}).data
    )
    response = client.get(f"/api/ingredients/{created['id']}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == created["id"]
    assert data["name"] == "Butter"
    assert data["location"] == "Dairy"
    assert data["recipes"] == []


def test_get_ingredient_by_id_404():
    client = _client()
    response = client.get(f"/api/ingredients/{uuid.uuid4()}")
    assert response.status_code == 404


def test_update_ingredient_success():
    client = _client()
    created = json.loads(_post_ingredient(client, {"name": "Oil"}).data)
    response = client.put(
        f"/api/ingredients/{created['id']}",
        json={
            "name": "Olive Oil",
            "default_unit": "tbsp",
            "location": "Pantry",
        },
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == created["id"]
    assert data["name"] == "Olive Oil"
    assert data["default_unit"] == "tbsp"
    assert data["location"] == "Pantry"


def test_update_ingredient_404():
    client = _client()
    response = client.put(
        f"/api/ingredients/{uuid.uuid4()}",
        json={"name": "Ghost"},
    )
    assert response.status_code == 404


def test_update_ingredient_duplicate_name_409():
    client = _client()
    first = json.loads(_post_ingredient(client, {"name": "Sugar"}).data)
    second = json.loads(_post_ingredient(client, {"name": "Honey"}).data)
    response = client.put(
        f"/api/ingredients/{second['id']}",
        json={"name": "Sugar"},
    )
    assert response.status_code == 409
    same = client.put(
        f"/api/ingredients/{first['id']}",
        json={"name": "Sugar", "default_unit": "cups"},
    )
    assert same.status_code == 200


def test_update_blank_name_400():
    client = _client()
    created = json.loads(_post_ingredient(client, {"name": "Cinnamon"}).data)
    response = client.put(
        f"/api/ingredients/{created['id']}",
        json={"name": "  "},
    )
    assert response.status_code == 400


def test_delete_ingredient_success():
    client = _client()
    created = json.loads(_post_ingredient(client, {"name": "Vanilla"}).data)
    response = client.delete(f"/api/ingredients/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/ingredients/{created['id']}").status_code == 404


def test_delete_ingredient_404():
    client = _client()
    response = client.delete(f"/api/ingredients/{uuid.uuid4()}")
    assert response.status_code == 404


def test_delete_ingredient_in_use_returns_409():
    client = _client()
    created = json.loads(_post_ingredient(client, {"name": "Eggs"}).data)
    crud.create_recipe(
        name="Omelette",
        instructions="Cook.",
        ingredients_data=[{"name": "Eggs", "quantity": 2, "unit": "pc"}],
    )
    response = client.delete(f"/api/ingredients/{created['id']}")
    assert response.status_code == 409
    data = json.loads(response.data)
    assert data["usage_count"] == 1
    get_resp = client.get(f"/api/ingredients/{created['id']}")
    assert get_resp.status_code == 200


def test_get_ingredient_info_removed():
    client = _client()
    _post_ingredient(client, {"name": "Cocoa"})
    response = client.get("/api/ingredients/info?name=Cocoa")
    assert response.status_code == 404


def test_get_ingredients_summary_removed():
    client = _client()
    response = client.get("/api/ingredients/summary")
    assert response.status_code == 404
