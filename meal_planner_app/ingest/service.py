"""Parse pasted text/HTML into a recipe draft. Does not persist."""

from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

from meal_planner_app.ingest.fetch import fetch_page
from meal_planner_app.ingest.html_extract import (
    extract_jsonld_recipe,
    extract_visible_text,
    jsonld_partial,
    looks_like_html,
)
from meal_planner_app.ingest.llm_client import OllamaClient
from meal_planner_app.ingest.prompts import (
    SYSTEM_EXTRACT,
    SYSTEM_SPLIT,
    extract_user_prompt,
    split_user_prompt,
)
from meal_planner_app.ingest.schema import ParsedIngredient, ParsedRecipe
from meal_planner_app.units import normalize_unit

MAX_TEXT_BYTES = 200 * 1024
MAX_LLM_CHARS = 8000

_LLM_OVERRIDE = None


def set_llm_client(client: Any) -> None:
    """Install (or clear) a process-wide LLM client. Tests pass a fake."""
    # pylint: disable=global-statement
    global _LLM_OVERRIDE
    _LLM_OVERRIDE = client


def get_llm_client() -> Any:
    """Return the override client, or OllamaClient.from_env()."""
    if _LLM_OVERRIDE is not None:
        return _LLM_OVERRIDE
    return OllamaClient.from_env()


_CANONICAL_UNITS = {
    "g": "g",
    "gram": "g",
    "grams": "g",
    "kg": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "ml": "ml",
    "millilitre": "ml",
    "milliliter": "ml",
    "millilitres": "ml",
    "milliliters": "ml",
    "l": "l",
    "litre": "l",
    "liter": "l",
    "litres": "l",
    "liters": "l",
}


class ParseError(Exception):
    """Base parse failure with an HTTP status for the API layer."""

    status_code = 400


class ParseValidationError(ParseError):
    """Bad request (empty, oversize, invalid URL)."""

    status_code = 400


class ParseUnusableError(ParseError):
    """Model/JSON-LD produced no name+instructions."""

    status_code = 422


def canonicalize_unit(unit: Optional[str]) -> str:
    """Map gram(s)/ml family to short forms; leave szt/op/ząbek unchanged."""
    normalized = normalize_unit(unit)
    if normalized in _CANONICAL_UNITS:
        return _CANONICAL_UNITS[normalized]
    return (unit or "").strip()


def remap_ingredient_name(name: str, catalog_names: Optional[Iterable[str]]) -> str:
    """Case-insensitive exact match onto an existing catalog name."""
    stripped = (name or "").strip()
    if not stripped:
        return stripped
    lookup = {item.casefold(): item for item in catalog_names or [] if item}
    return lookup.get(stripped.casefold(), stripped)


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def ingredients_from_payload(
    payload: Dict[str, Any], catalog_names: Optional[Iterable[str]]
) -> List[ParsedIngredient]:
    raw = payload.get("ingredients") if isinstance(payload, dict) else None
    if not isinstance(raw, list):
        return []
    result: List[ParsedIngredient] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = remap_ingredient_name(_as_str(item.get("name")), catalog_names)
        if not name:
            continue
        result.append(
            ParsedIngredient(
                name=name,
                quantity=_as_str(item.get("quantity")),
                unit=canonicalize_unit(item.get("unit")),
                location="",
            )
        )
    return result


def _validate_text(text: Optional[str]) -> str:
    if text is None or not str(text).strip():
        raise ParseValidationError("text or url is required")
    raw = str(text)
    if len(raw.encode("utf-8")) > MAX_TEXT_BYTES:
        raise ParseValidationError("text is too large")
    return raw


def _validate_source_url(source_url: Optional[str]) -> str:
    if source_url is None or not str(source_url).strip():
        return ""
    url = str(source_url).strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ParseValidationError("source_url must be an http(s) URL")
    return url


def _usable_jsonld(partial: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not partial:
        return None
    name = (partial.get("name") or "").strip()
    instructions = (partial.get("instructions") or "").strip()
    if not name or not instructions:
        return None
    return {
        "name": name,
        "description": partial.get("description") or "",
        "instructions": instructions,
        "ingredient_lines": partial.get("ingredient_lines") or [],
    }


def parse_recipe(  # pylint: disable=too-many-arguments
    text: Optional[str],
    source_url: str = "",
    llm: Any = None,
    catalog_names: Optional[Iterable[str]] = None,
) -> ParsedRecipe:
    """Turn pasted text/HTML (or a fetched URL) into a draft. Never writes the DB."""
    source = _validate_source_url(source_url)
    if text is None or not str(text).strip():
        if not source:
            raise ParseValidationError("text or url is required")
        fetched = fetch_page(source)
        raw = fetched.text
        source = source or fetched.source_url
    else:
        raw = _validate_text(text)
    client = llm if llm is not None else get_llm_client()
    model = getattr(client, "model", "") or ""

    node = extract_jsonld_recipe(raw) if looks_like_html(raw) else None
    core = _usable_jsonld(jsonld_partial(node) if node else None)

    if core and core["ingredient_lines"]:
        payload = client.complete_json(
            SYSTEM_SPLIT, split_user_prompt(core["ingredient_lines"])
        )
        recipe = ParsedRecipe(
            name=core["name"],
            description=core["description"],
            instructions=core["instructions"],
            source_url=source,
            ingredients=ingredients_from_payload(payload, catalog_names),
            parser="jsonld+llm",
            model=model,
        )
    elif core:
        recipe = ParsedRecipe(
            name=core["name"],
            description=core["description"],
            instructions=core["instructions"],
            source_url=source,
            ingredients=[],
            parser="jsonld",
            model="",
        )
    else:
        visible = extract_visible_text(raw)
        if len(visible) > MAX_LLM_CHARS:
            visible = visible[:MAX_LLM_CHARS]
        payload = client.complete_json(SYSTEM_EXTRACT, extract_user_prompt(visible))
        recipe = ParsedRecipe(
            name=_as_str(payload.get("name") if isinstance(payload, dict) else ""),
            description=_as_str(
                payload.get("description") if isinstance(payload, dict) else ""
            ),
            instructions=_as_str(
                payload.get("instructions") if isinstance(payload, dict) else ""
            ),
            source_url=source,
            ingredients=ingredients_from_payload(
                payload if isinstance(payload, dict) else {}, catalog_names
            ),
            parser="llm",
            model=model,
        )

    if not recipe.is_usable():
        raise ParseUnusableError("could not extract a recipe name and instructions")
    return recipe
