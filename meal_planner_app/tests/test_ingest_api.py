"""API tests for POST /api/recipes/parse (draft only, no persistence)."""

import json

from meal_planner_app.main import app
from meal_planner_app import crud
from meal_planner_app.ingest import service as ingest_service
from meal_planner_app.ingest.llm_client import LlmTimeoutError, LlmUnavailableError
from meal_planner_app.tests.test_ingest_html import POLISH_JSONLD_HTML
from meal_planner_app.tests.test_ingest_service import FakeLlm


def _client():
    crud.reset_recipes_db()
    return app.test_client()


def setup_function():
    ingest_service.set_llm_client(None)


def teardown_function():
    ingest_service.set_llm_client(None)


def test_parse_jsonld_returns_draft_and_does_not_persist():
    ingest_service.set_llm_client(
        FakeLlm(
            {
                "ingredients": [
                    {"name": "filet z kurczaka", "quantity": "500", "unit": "g"},
                    {"name": "cebula", "quantity": "2", "unit": "szt"},
                ]
            }
        )
    )
    crud.create_master_ingredient(name="Cebula", default_unit="szt")
    client = _client()
    # reset_recipes_db in _client wipes Cebula — recreate after
    crud.create_master_ingredient(name="Cebula", default_unit="szt")
    before_recipes = len(crud.list_recipes())
    before_ings = len(crud.list_unique_ingredient_names())

    response = client.post(
        "/api/recipes/parse",
        json={
            "text": POLISH_JSONLD_HTML,
            "source_url": "https://aniagotuje.pl/przepis/kurczak",
        },
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Kurczak z jarmużem i ryżem"
    assert data["source_url"] == "https://aniagotuje.pl/przepis/kurczak"
    assert data["meta"]["parser"] == "jsonld+llm"
    names = [row["name"] for row in data["ingredients"]]
    assert "Cebula" in names
    assert len(crud.list_recipes()) == before_recipes
    assert len(crud.list_unique_ingredient_names()) == before_ings


def test_parse_missing_text_400():
    ingest_service.set_llm_client(FakeLlm({"name": "x", "instructions": "y"}))
    client = _client()
    assert client.post("/api/recipes/parse", json={}).status_code == 400
    assert client.post("/api/recipes/parse", json={"text": "  "}).status_code == 400


def test_parse_invalid_source_url_400():
    ingest_service.set_llm_client(FakeLlm({"name": "x", "instructions": "y"}))
    client = _client()
    response = client.post(
        "/api/recipes/parse",
        json={"text": "zupa", "source_url": "ftp://x"},
    )
    assert response.status_code == 400


def test_parse_unusable_422():
    ingest_service.set_llm_client(
        FakeLlm({"name": "", "instructions": "", "ingredients": []})
    )
    client = _client()
    response = client.post("/api/recipes/parse", json={"text": "reklama bloga"})
    assert response.status_code == 422
    body = json.loads(response.data)
    assert "error" in body


def test_parse_llm_down_503():
    ingest_service.set_llm_client(FakeLlm(LlmUnavailableError("down")))
    client = _client()
    response = client.post("/api/recipes/parse", json={"text": "zupa. gotować."})
    assert response.status_code == 503


def test_parse_llm_timeout_504():
    ingest_service.set_llm_client(FakeLlm(LlmTimeoutError("slow")))
    client = _client()
    response = client.post("/api/recipes/parse", json={"text": "zupa. gotować."})
    assert response.status_code == 504


def test_parse_without_llm_configured_503(monkeypatch):
    ingest_service.set_llm_client(None)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    client = _client()
    response = client.post("/api/recipes/parse", json={"text": "zupa. gotować."})
    assert response.status_code == 503
