#!/usr/bin/env python3
"""Legacy migration from przepisy_tmp.odb (or fallback to bundled recipes).

This module is called by start_and_seed.sh when /app/legacy/przepisy_tmp.odb exists.
It extracts recipe titles + source URLs + best-effort ingredients from the
legacy HSQL/ODB file using zip + heuristics (no Java/DB tools needed), then
seeds them via the API.

Falls back to a small bundled LEGACY_RECIPES list if extraction yields nothing.
"""

import json
import logging
import urllib.request
import urllib.error
import zipfile
import re
import os
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:5000/api"


def get_recipes() -> List[Dict[str, Any]]:
    """Fetch existing recipes from the running backend API."""
    try:
        with urllib.request.urlopen(f"{API_BASE_URL}/recipes", timeout=5) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        logger.error("API not reachable. Is backend running? (%s)", e)
    return None


def create_recipe(recipe: Dict[str, Any]) -> None:
    """POST a single recipe to the API (same shape as seed_db)."""
    data = json.dumps(recipe).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE_URL}/recipes",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201):
                created = json.loads(resp.read().decode("utf-8"))
                logger.info(
                    "Created recipe: %s", created.get("name", recipe.get("name"))
                )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Failed to create recipe %s: %s", recipe.get("name"), e)


# A small bundled fallback (real data lives in the .odb).
# These are examples extracted from the original legacy set.
LEGACY_RECIPES: List[Dict[str, Any]] = [
    {
        "name": "Drobiowe pulpeciki idealne na początek BLW",
        "source_url": "https://alaantkoweblw.pl/drobiowe-pulpeciki-idealne-na-poczatek-blw-2/",
        "instructions": "See source_url for full original instructions. (auto-migrated from .odb)",
        "description": "BLW friendly",
        "ingredients": [
            {"name": "Mielone indyk", "quantity": "400", "unit": "g"},
        ],
    },
    {
        "name": "Kurczak z dynią",
        "source_url": "https://aniagotuje.pl/przepis/kurczak-z-dynia",
        "instructions": "See full recipe at source_url. (Migrated from przepisy_tmp.odb)",
        "description": "",
        "ingredients": [
            {"name": "Kurczak", "quantity": "500", "unit": "g"},
            {"name": "Dynia", "quantity": "400", "unit": "g"},
            {"name": "Cebula", "quantity": "1", "unit": "szt"},
        ],
    },
    {
        "name": "Zapiekanka z kaszą jęczmienną i warzywami",
        "source_url": "http://naszakasza.pl/przepisy/zapiekanka-kasza-jeczmienna-warzywami/",
        "instructions": "See full recipe at source_url. (Migrated from przepisy_tmp.odb)",
        "description": "",
        "ingredients": [
            {"name": "Kasza jęczmienna", "quantity": "1", "unit": "szklanka"},
            {"name": "Marchew", "quantity": "2", "unit": "szt"},
            {"name": "Cukinia", "quantity": "1", "unit": "szt"},
        ],
    },
    {
        "name": "Zupa jesienna",
        "source_url": "https://www.dorotasmakuje.com/2014/10/zupa-jesienna/",
        "instructions": "See full recipe at source_url. (Migrated from przepisy_tmp.odb)",
        "description": "",
        "ingredients": [
            {"name": "Dynia", "quantity": "500", "unit": "g"},
            {"name": "Marchew", "quantity": "3", "unit": "szt"},
        ],
    },
    {
        "name": "Szybkie curry pomidorowe z kurczakiem",
        "source_url": "https://alaantkoweblw.pl/szybkie-curry-pomidorowe-z-kurczakiem-alaantkoweblw/",  # pylint: disable=line-too-long
        "instructions": "See full recipe at source_url. (Migrated from przepisy_tmp.odb)",
        "description": "",
        "ingredients": [
            {"name": "Kurczak", "quantity": "400", "unit": "g"},
            {"name": "Pomidory", "quantity": "400", "unit": "g"},
        ],
    },
]


def _safe_decode(raw: bytes) -> str:
    """Decode legacy ODB data trying Polish-friendly encodings first.

    HSQL/OO Base .odb content (often in 'data' or 'script' members) may be
    UTF-8, Windows-1250 or ISO-8859-2 for Polish diacritics (ąęłńóśźż etc.).
    Falls back to latin1 ignore to avoid total failure.
    """
    encodings = ["utf-8", "utf-8-sig", "cp1250", "windows-1250", "iso-8859-2", "latin1"]
    for enc in encodings:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin1", errors="ignore")


def _extract_ingredients(
    text: str, start_pos: int = 0, max_ingredients: int = 12
) -> List[Dict[str, Any]]:
    """Heuristic extraction of ingredients from the decoded ODB text.

    Looks for common quantity + unit + name patterns (supports Polish units and
    diacritics). This is best-effort because the legacy .odb is just a raw
    HSQL dump without a proper schema parser.
    """
    window = text[start_pos : start_pos + 3000]
    # Patterns like: 400 g mielone indyk , 2 łyżki mąki , 1,5 szklanki mleka
    # Supports Polish units and accented names.
    ing_re = re.compile(
        r"(\d+[\.,]?\d*)\s*"
        r"(g|kg|ml|l|łyżk[aię]|łyżeczki|szklank[ai]|szt|opak|kostk[ai]|pęczek|ząbek|plaster)?\s*"
        r"([A-Za-ząćęłńóśźż][A-Za-ząćęłńóśźż0-9 \-]{2,40})",
        re.IGNORECASE,
    )
    ingredients: List[Dict[str, Any]] = []
    seen_names = set()
    for m in ing_re.finditer(window):
        qty = m.group(1).replace(",", ".")
        unit = (m.group(2) or "").strip()
        name = m.group(3).strip()
        # Clean up cases where the pattern over-captured (e.g. next qty got attached)
        name = re.sub(r"\s+\d.*$", "", name).strip()
        key = name.lower()
        if (
            len(name) > 2
            and key not in seen_names
            and not key.startswith(("http", "www", "insert"))
        ):
            seen_names.add(key)
            ingredients.append(
                {
                    "name": name,
                    "quantity": qty,
                    "unit": unit,
                }
            )
            if len(ingredients) >= max_ingredients:
                break
    return ingredients


# pylint: disable=too-many-locals
def extract_from_odb(
    odb_path: str = "/app/legacy/przepisy_tmp.odb",
) -> List[Dict[str, Any]]:
    """Best-effort extraction of title + URL + ingredients from the .odb zip file.

    The legacy Base DB stores content in a zip. We look for a 'data' (or script)
    member, try proper encodings for Polish signs, and use an improved regex
    heuristic that supports Polish diacritics in titles + http urls.
    Ingredients are extracted with a secondary heuristic for qty + unit + name.
    """
    if not os.path.exists(odb_path):
        return []

    recs: List[Dict[str, Any]] = []
    seen = set()

    try:
        with zipfile.ZipFile(odb_path, "r") as z:
            # Look for a data file (common locations inside HSQL/ODB). Also consider 'script'.
            candidates = [
                n
                for n in z.namelist()
                if any(k in n.lower() for k in ("data", "script"))
                or n.endswith(("data", "script"))
            ]
            if not candidates:
                candidates = z.namelist()[:3]  # fallback

            for member in candidates:
                try:
                    raw = z.read(member)
                    text = _safe_decode(raw)
                except Exception:  # pylint: disable=broad-exception-caught
                    continue

                # Heuristic: Title-like string (supporting Polish letters) followed later by a URL.
                # Polish letter support prevents truncation/mangling on ąęł etc.
                polish = "AĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻa-ząćęłńóśźż"
                control = "\x00-\x1f"
                # Build pattern avoiding f-string {N,M} quantifier conflict with format {}
                title_re = (
                    "(["
                    + polish
                    + "]["
                    + polish
                    + "0-9 ,.\\-':()]{4,100}["
                    + polish
                    + "0-9])"
                )
                url_re = "(https?://[^\\s" + control + ",]{15,150})"
                pattern = re.compile(
                    title_re + r"\s*.*?" + url_re,
                    re.IGNORECASE,
                )
                for m in pattern.finditer(text):
                    title = m.group(1).strip()
                    url = m.group(2).strip()

                    # Clean control chars + collapse whitespace
                    title = re.sub(r"[\x00-\x1f]", " ", title)
                    title = re.sub(r"\s+", " ", title).strip()

                    # Skip junk captures (binary fragments, SQL keywords, urls as title, too short)
                    low = title.lower()
                    if len(title) < 6 or low.startswith(
                        (
                            "http",
                            "www",
                            "insert",
                            "select",
                            "create",
                            "update",
                            "delete",
                        )
                    ):
                        continue
                    if url not in seen:
                        seen.add(url)
                        # Try to pull ingredients from context after this recipe entry
                        ingredients = _extract_ingredients(text, m.end())
                        recs.append(
                            {
                                "name": title,
                                "source_url": url,
                                "instructions": "See source_url for full original instructions. (auto-migrated from .odb)",  # pylint: disable=line-too-long
                                "description": "Migrated from legacy przepisy_tmp.odb",
                                "ingredients": ingredients,
                            }
                        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Could not parse ODB %s: %s", odb_path, e)
        return []

    if recs:
        logger.info("Extracted %d recipes from ODB", len(recs))
    return recs


def seed_from_legacy(odb_path: str = "/app/legacy/przepisy_tmp.odb") -> None:
    """Seed using ODB if available, else bundled LEGACY_RECIPES.

    Always safe to call; it checks whether the DB is already populated.
    """
    existing = get_recipes()
    if existing is None:
        logger.error("API not reachable. Is backend running?")
        return

    if existing:
        logger.info(
            "DB has %d recipes already. Skipping (for new program: remove data or force).",
            len(existing),
        )
        return

    recipes = extract_from_odb(odb_path) or LEGACY_RECIPES

    logger.info("Seeding %d recipes from legacy data...", len(recipes))
    for r in recipes:
        create_recipe(r)

    logger.info("Legacy migration seed completed.")


if __name__ == "__main__":
    seed_from_legacy()
