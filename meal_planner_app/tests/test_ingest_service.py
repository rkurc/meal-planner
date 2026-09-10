"""Parse orchestration: JSON-LD first, LLM leftovers, no persistence."""

import pytest

from meal_planner_app import crud
from meal_planner_app.ingest.llm_client import LlmTimeoutError, LlmUnavailableError
from meal_planner_app.ingest.service import (
    ParseUnusableError,
    ParseValidationError,
    parse_recipe,
)
from meal_planner_app.tests.test_ingest_html import POLISH_JSONLD_HTML


class FakeLlm:
    """Records prompts and returns a canned JSON object."""

    def __init__(self, payload, model="qwen2.5:1.5b"):
        self.payload = payload
        self.model = model
        self.calls = []

    def complete_json(self, system, user):
        self.calls.append({"system": system, "user": user})
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


def test_jsonld_complete_only_asks_llm_to_split_ingredients():
    llm = FakeLlm(
        {
            "ingredients": [
                {"name": "filet z kurczaka", "quantity": "500", "unit": "g"},
                {"name": "cebula", "quantity": "2", "unit": "szt"},
                {"name": "sól", "quantity": "", "unit": ""},
            ]
        }
    )
    draft = parse_recipe(
        POLISH_JSONLD_HTML,
        source_url="https://aniagotuje.pl/przepis/kurczak",
        llm=llm,
        catalog_names=["Cebula"],
    )
    assert draft.name == "Kurczak z jarmużem i ryżem"
    assert "1. Drobno pokroić cebulę" in draft.instructions
    assert draft.source_url == "https://aniagotuje.pl/przepis/kurczak"
    assert draft.parser == "jsonld+llm"
    assert [(i.name, i.quantity, i.unit) for i in draft.ingredients] == [
        ("filet z kurczaka", "500", "g"),
        ("Cebula", "2", "szt"),
        ("sól", "", ""),
    ]
    assert len(llm.calls) == 1
    assert "500 g filet z kurczaka" in llm.calls[0]["user"]
    assert "Kurczak z jarmużem i ryżem" not in llm.calls[0]["user"]


def test_plain_text_uses_full_llm_extract_and_ignores_model_source():
    llm = FakeLlm(
        {
            "name": "Zupa",
            "description": "",
            "instructions": "Gotować 20 min.",
            "source_url": "https://hallucinated.example/",
            "ingredients": [{"name": "woda", "quantity": "1", "unit": "l"}],
        }
    )
    draft = parse_recipe(
        "Zupa. Składniki: 1 l wody. Gotować 20 min.",
        source_url="https://example.com/zupa",
        llm=llm,
    )
    assert draft.name == "Zupa"
    assert draft.instructions == "Gotować 20 min."
    assert draft.source_url == "https://example.com/zupa"
    assert draft.parser == "llm"
    assert draft.ingredients[0].name == "woda"
    assert draft.ingredients[0].unit == "l"


def test_canonicalizes_mass_volume_units():
    llm = FakeLlm(
        {
            "name": "Chleb",
            "instructions": "Upiec.",
            "ingredients": [{"name": "mąka", "quantity": "500", "unit": "grams"}],
        }
    )
    draft = parse_recipe("Chleb. 500 grams mąka. Upiec.", llm=llm)
    assert draft.ingredients[0].unit == "g"


def test_empty_text_is_validation_error():
    with pytest.raises(ParseValidationError):
        parse_recipe("   ", llm=FakeLlm({}))
    with pytest.raises(ParseValidationError):
        parse_recipe("", llm=FakeLlm({}))


def test_oversize_text_is_validation_error():
    with pytest.raises(ParseValidationError):
        parse_recipe("x" * (200 * 1024 + 1), llm=FakeLlm({}))


def test_invalid_source_url_is_validation_error():
    with pytest.raises(ParseValidationError):
        parse_recipe("zupa", source_url="javascript:alert(1)", llm=FakeLlm({}))
    with pytest.raises(ParseValidationError):
        parse_recipe("zupa", source_url="not-a-url", llm=FakeLlm({}))


def test_unusable_llm_result_is_422():
    llm = FakeLlm({"name": "", "instructions": "", "ingredients": []})
    with pytest.raises(ParseUnusableError):
        parse_recipe("jakiś tekst bez przepisu", llm=llm)


def test_llm_unavailable_bubbles_up():
    llm = FakeLlm(LlmUnavailableError("ollama down"))
    with pytest.raises(LlmUnavailableError):
        parse_recipe("zupa. gotować.", llm=llm)


def test_llm_timeout_bubbles_up():
    llm = FakeLlm(LlmTimeoutError("timeout"))
    with pytest.raises(LlmTimeoutError):
        parse_recipe("zupa. gotować.", llm=llm)


def test_parse_does_not_write_catalog_or_recipes():
    llm = FakeLlm(
        {
            "name": "Naleśniki",
            "instructions": "Smażyć.",
            "ingredients": [{"name": "mąka", "quantity": "200", "unit": "g"}],
        }
    )
    before_r = len(crud.list_recipes())
    before_i = len(crud.list_unique_ingredient_names())
    parse_recipe("Naleśniki. 200 g mąki. Smażyć.", llm=llm)
    assert len(crud.list_recipes()) == before_r
    assert len(crud.list_unique_ingredient_names()) == before_i
