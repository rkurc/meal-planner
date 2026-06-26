#!/usr/bin/env python3
"""Legacy migration (recommended 2-step or legacy .odb).

Recommended reliable path (2-step):
1. On Windows (with LibreOffice Base / OpenOffice Base):
   - Open przepisy_tmp.odb
   - Export the main recipes table to CSV (UTF-8, headers, comma or semicolon delimiter).
   - See README for exact export steps and expected columns.
2. Place recipes.csv (or przepisy.csv) in the legacy/ dir (next to the .odb if you want).
   Run this module (via start_and_seed.sh or manually). It will prefer the CSV.

CSV gives clean, editable, deterministic data (no binary scraping).

Still supports direct .odb extraction via heuristics (zip + regex) as fallback.
Falls back to bundled LEGACY_RECIPES.

Ingestion always happens via the live /api/recipes (same as seed_db).
"""

import csv
import json
import logging
import urllib.request
import urllib.error
import zipfile
import re
import os
from collections import defaultdict
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
            {
                "name": "Mielone indyk",
                "quantity": "400",
                "unit": "g",
                "location_id": None,
            },
        ],
    },
    {
        "name": "Kurczak z dynią",
        "source_url": "https://aniagotuje.pl/przepis/kurczak-z-dynia",
        "instructions": "See full recipe at source_url. (Migrated from przepisy_tmp.odb)",
        "description": "",
        "ingredients": [
            {"name": "Kurczak", "quantity": "500", "unit": "g", "location_id": None},
            {"name": "Dynia", "quantity": "400", "unit": "g", "location_id": None},
            {"name": "Cebula", "quantity": "1", "unit": "szt", "location_id": None},
        ],
    },
    {
        "name": "Zapiekanka z kaszą jęczmienną i warzywami",
        "source_url": "http://naszakasza.pl/przepisy/zapiekanka-kasza-jeczmienna-warzywami/",
        "instructions": "See full recipe at source_url. (Migrated from przepisy_tmp.odb)",
        "description": "",
        "ingredients": [
            {
                "name": "Kasza jęczmienna",
                "quantity": "1",
                "unit": "szklanka",
                "location_id": None,
            },
            {"name": "Marchew", "quantity": "2", "unit": "szt", "location_id": None},
            {"name": "Cukinia", "quantity": "1", "unit": "szt", "location_id": None},
        ],
    },
    {
        "name": "Zupa jesienna",
        "source_url": "https://www.dorotasmakuje.com/2014/10/zupa-jesienna/",
        "instructions": "See full recipe at source_url. (Migrated from przepisy_tmp.odb)",
        "description": "",
        "ingredients": [
            {"name": "Dynia", "quantity": "500", "unit": "g", "location_id": None},
            {"name": "Marchew", "quantity": "3", "unit": "szt", "location_id": None},
        ],
    },
    {
        "name": "Szybkie curry pomidorowe z kurczakiem",
        "source_url": "https://alaantkoweblw.pl/szybkie-curry-pomidorowe-z-kurczakiem-alaantkoweblw/",  # pylint: disable=line-too-long
        "instructions": "See full recipe at source_url. (Migrated from przepisy_tmp.odb)",
        "description": "",
        "ingredients": [
            {"name": "Kurczak", "quantity": "400", "unit": "g", "location_id": None},
            {"name": "Pomidory", "quantity": "400", "unit": "g", "location_id": None},
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


def _looks_like_junk(name: str) -> bool:  # pylint: disable=too-many-return-statements
    """Return True for names that are clearly noise from binary/encoded dump content.

    Rejects names containing digits (after clean step), long id-like alphanum,
    uppercase runs, file extension words, urls, insufficient letters.
    """
    if not name:
        return True
    n = name.strip()
    if len(n) < 3 or len(n) > 35:
        return True
    # Any digits left in name after qty stripping -> almost always junk from dump
    if re.search(r"\d", n):
        return True
    # Long alphanumeric runs without spaces (base64, hashes, guids fragments)
    if re.search(r"[A-Za-z0-9]{9,}", n):
        return True
    # Long uppercase runs (rare for food names)
    if re.search(r"[A-Z]{4,}", n):
        return True
    # File/web junk words (even without dot)
    if re.search(r"\.(html|htm|php|js|css|data|odb|log)\b|https?://", n, re.IGNORECASE):
        return True
    junk_words = ("html", "htm", "php", "script", "data", "odb", "log")
    if any(w in n.lower() for w in junk_words):
        return True
    # Too many non word chars
    if len(re.findall(r"[^A-Za-ząćęłńóśźż0-9 -]", n)) > 2:
        return True
    # Insufficient letters
    alpha = sum(c.isalpha() for c in n)
    if alpha < 2:
        return True
    return False


def parse_ingredient_line(line: str) -> Dict[str, Any]:
    """Parse one ingredient line into {name, quantity, unit}.

    Supports common patterns like "500 g kurczak", "2 łyżki oliwy", "1 szt jajko".
    Falls back to treating the whole line as the name (quantity/unit empty).
    Used for both CSV exports and legacy textarea-style data.
    """
    line = line.strip()
    if not line:
        return {"name": "", "quantity": "", "unit": ""}

    # Flexible qty + optional unit + name (Polish + some English units)
    m = re.match(
        r"^(\d+[\.,]?\d*)\s*"
        r"(g|kg|ml|l|łyżk[aię]|łyżeczki|szklank[ai]|szt|opak|kostk[ai]|pęczek|ząbek|plaster|"
        r"cup|cups|tbsp|tsp|oz|lb|piece|pieces)?\s*"
        r"(.+)$",
        line,
        re.IGNORECASE,
    )
    if m:
        qty = m.group(1).replace(",", ".").strip()
        unit = (m.group(2) or "").strip()
        name = m.group(3).strip()
        if name:
            return {"name": name, "quantity": qty, "unit": unit}

    # Fallback: whole line is the name (matches old legacy textarea behavior)
    return {
        "name": line,
        "quantity": "",
        "unit": "",
        "location_id": None,
        "location": None,
    }


def parse_ingredients_from_text(text: str) -> List[Dict[str, Any]]:
    """Turn a block of ingredient text (newlines or | separated) into structured list."""
    if not text:
        return []
    # Normalize separators
    normalized = text.replace("|", "\n").replace(";", "\n")
    lines = [l.strip() for l in normalized.splitlines() if l.strip()]
    return [parse_ingredient_line(line) for line in lines]


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
            and not _looks_like_junk(name)
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
            # Prefer 'script' (often contains readable SQL INSERTs for HSQL) over raw 'data'.
            # Fall back to data or first few members.
            candidates = [
                n
                for n in z.namelist()
                if any(k in n.lower() for k in ("script",)) or n.endswith(("script",))
            ] or [
                n
                for n in z.namelist()
                if any(k in n.lower() for k in ("data",)) or n.endswith(("data",))
            ]
            if not candidates:
                candidates = z.namelist()[:3]  # fallback

            for member in candidates:
                try:
                    raw = z.read(member)
                    text = _safe_decode(raw)
                    # Collapse control chars globally so embedded nulls etc don't truncate
                    # titles or create weird splits in the heuristic scan.
                    text = re.sub(r"[\x00-\x1f]+", " ", text)
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

                    # Clean control chars + collapse whitespace (controls already normalized above)
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


def extract_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """Import recipes from a user-exported CSV (the recommended 2-step path).

    Expected columns (case-insensitive, common Polish/English variants supported):
      - name / tytul / tytuł / nazwa
      - source_url / url / zrodlo / źródło / source
      - description / opis (optional)
      - instructions / instrukcje (optional)
      - ingredients / skladniki / składniki / sklad (text, one ingredient per line)

    Use UTF-8 when exporting from Calc/Base. Newlines inside the ingredients cell are supported.
    """
    if not os.path.exists(csv_path):
        return []

    recs: List[Dict[str, Any]] = []

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            # Try common delimiters if not auto-detected well
            sample = f.read(4096)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=",;|\t")
            reader = csv.DictReader(f, dialect=dialect)

            for row in reader:
                # Build case-insensitive lookup
                lower_row = {
                    (k or "").strip().lower(): (v or "").strip() for k, v in row.items()
                }

                name = (
                    lower_row.get("name")
                    or lower_row.get("tytul")
                    or lower_row.get("tytuł")
                    or lower_row.get("nazwa")
                    or lower_row.get("recipe")
                    or ""
                )
                if not name:
                    continue

                source_url = (
                    lower_row.get("source_url")
                    or lower_row.get("url")
                    or lower_row.get("zrodlo")
                    or lower_row.get("źródło")
                    or lower_row.get("source")
                    or lower_row.get("link")
                    or ""
                )

                description = (
                    lower_row.get("description")
                    or lower_row.get("opis")
                    or "Migrated from legacy CSV export"
                )

                instructions = (
                    lower_row.get("instructions")
                    or lower_row.get("instrukcje")
                    or "See source_url for full original instructions. (migrated from CSV)"
                )

                ing_text = (
                    lower_row.get("ingredients")
                    or lower_row.get("skladniki")
                    or lower_row.get("składniki")
                    or lower_row.get("sklad")
                    or lower_row.get("ingredient")
                    or ""
                )

                ingredients = parse_ingredients_from_text(ing_text)

                recs.append(
                    {
                        "name": name,
                        "source_url": source_url,
                        "description": description,
                        "instructions": instructions,
                        "ingredients": ingredients,
                    }
                )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Could not parse CSV %s: %s", csv_path, e)
        return []

    if recs:
        logger.info("Loaded %d recipes from CSV", len(recs))
    return recs


# pylint: disable=too-many-branches,too-many-statements
def extract_from_csvs(
    base_dir: str = "/app/legacy",
) -> List[Dict[str, Any]]:
    """Import from the detailed relational CSV export (przepisy + skladniki + produkty + jednostki).

    This is the proper normalized export from the legacy Base DB:
      - przepisy.csv     -> recipes (id, nazwa, przepis=instructions, liczbaPorcji)
      - skladniki.csv    -> join (idPrzepisu, idProduktu, liczba=quantity)
      - produkty.csv     -> master ingredients (id, nazwa, idJednostki)
      - jednostki.csv    -> units (idJednostki, nazwa)   e.g. g, ml, szt, op, kg, ząbek

    The app model has no global product table, so we denormalize product name + its default unit
    into each recipe's ingredient list.

    URLs are frequently stored inside the "przepis" text field; we extract the first one to
    source_url and provide a clean placeholder for instructions when the field was only a URL.
    """
    files = {
        "przepisy": os.path.join(base_dir, "przepisy.csv"),
        "skladniki": os.path.join(base_dir, "skladniki.csv"),
        "produkty": os.path.join(base_dir, "produkty.csv"),
        "jednostki": os.path.join(base_dir, "jednostki.csv"),
    }
    if not all(
        os.path.exists(f)
        for f in (files["przepisy"], files["skladniki"], files["produkty"])
    ):
        return []

    try:
        # Units
        jednostki = {}
        if os.path.exists(files["jednostki"]):
            with open(files["jednostki"], newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    jednostki[row["idJednostki"]] = row["nazwa"]

        # Locations (for grouping by lokalizacje)
        lokalizacje = {}
        lok_path = os.path.join(base_dir, "lokalizacje.csv")
        if os.path.exists(lok_path):
            with open(lok_path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    lokalizacje[row["idLokalizacji"]] = row["lokalizacja"]

        # Products
        produkty = {}
        with open(files["produkty"], newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                pid = row["id"]
                jid = row.get("idJednostki", "")
                lid = row.get("idLokalizacji", "")
                produkty[pid] = {
                    # Master ingredient/product from produkty.csv:
                    #   id = unique key
                    #   nazwa = name
                    #   idJednostki = unit reference (look up in jednostki.csv)
                    #   idLokalizacji = location id (from lokalizacje.csv)
                    "nazwa": row.get("nazwa", "").strip(),
                    "idJednostki": jid,
                    "jednostka": jednostki.get(jid, ""),
                    "idLokalizacji": lid,
                    "location": lokalizacje.get(lid, ""),
                }

        # Skladniki grouped by recipe
        sklad_by_rid: Dict[str, List[Dict]] = defaultdict(list)
        with open(files["skladniki"], newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                sklad_by_rid[row["idPrzepisu"]].append(row)

        # Recipes
        recs: List[Dict[str, Any]] = []
        url_re = re.compile(r"https?://[^\s,)]+")
        with open(files["przepisy"], newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rid = row.get("id", "")
                name = (row.get("nazwa") or "").strip()
                if not name:
                    continue

                instr = row.get("przepis", "") or ""
                porcje = (row.get("liczbaPorcji") or "").strip()

                # Extract first URL (common pattern in this export)
                m = url_re.search(instr)
                source_url = m.group(0).rstrip(".,") if m else ""

                # Clean instructions if the field was primarily/only the source URL
                instructions = instr
                if source_url and instr.strip().startswith("http"):
                    instructions = "See source_url for full original instructions. (auto-migrated from przepisy CSV)"  # pylint: disable=line-too-long

                description = "Migrated from legacy przepisy CSV export"
                if porcje:
                    description += f" (porcje: {porcje})"

                # Build ingredients via join
                # Each recipe ingredient (from skladniki.csv) links a recipe to a product:
                #   - name = produkt.nazwa
                #   - quantity = skladniki.liczba   (the amount; not stored on the master produkt)
                #   - unit = resolved from produkt.idJednostki via jednostki.csv
                #   - location_id = produkt.idLokalizacji
                ingredients: List[Dict[str, Any]] = []
                for s in sklad_by_rid.get(rid, []):
                    pid = s.get("idProduktu", "")
                    p = produkty.get(pid, {})
                    qty = (s.get("liczba") or "").strip()
                    unit = p.get("jednostka", "")
                    iname = p.get("nazwa", "")
                    if iname:
                        ingredients.append(
                            {
                                "name": iname,
                                "quantity": qty,
                                "unit": unit,
                                "location_id": p.get("idLokalizacji") or None,
                                "location": p.get("location") or None,
                            }
                        )

                recs.append(
                    {
                        "name": name,
                        "source_url": source_url,
                        "description": description,
                        "instructions": instructions,
                        "ingredients": ingredients,
                    }
                )

        if recs:
            logger.info(
                "Extracted %d recipes from relational CSV set in %s",
                len(recs),
                base_dir,
            )
        return recs
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Failed to parse relational CSVs in %s: %s", base_dir, e)
        return []


def seed_from_legacy(
    odb_path: str = "/app/legacy/przepisy_tmp.odb",
    csv_path: str = "/app/legacy/recipes.csv",
    base_dir: str = "/app/legacy",
) -> None:
    """Seed using the best available legacy data.

    Priority:
    1. Relational CSVs (przepisy.csv + skladniki.csv + produkty.csv) in base_dir
    2. Flat CSV
    3. .odb heuristic
    4. Bundled LEGACY_RECIPES
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

    recipes: List[Dict[str, Any]] = []

    # 1. Best: the detailed relational CSV export the user provided
    #    (przepisy.csv + skladniki.csv + produkty.csv + jednostki.csv)
    rel_files = ["przepisy.csv", "skladniki.csv", "produkty.csv"]
    if all(os.path.exists(os.path.join(base_dir, f)) for f in rel_files):
        recipes = extract_from_csvs(base_dir)
        if recipes:
            logger.info("Using relational CSV set from %s", base_dir)

    # 2. Fallback: a flat user-exported recipes.csv (from previous 2-step advice)
    if not recipes:
        csv_candidates = [
            csv_path,
            os.path.join(base_dir, "przepisy.csv"),  # might be flat in some exports
            os.path.join(base_dir, "recipes.csv"),
            os.path.join(base_dir, "recipes_export.csv"),
            os.path.join(base_dir, "legacy.csv"),
        ]
        for cand in csv_candidates:
            if (
                os.path.exists(cand) and "skladniki.csv" not in cand
            ):  # avoid misusing relational
                recipes = extract_from_csv(cand)
                if recipes:
                    logger.info("Using flat CSV export: %s", cand)
                    break

    # 3. Fallback: direct .odb (heuristic, may contain junk from binary data)
    if not recipes:
        recipes = extract_from_odb(odb_path)
        if recipes:
            logger.warning(
                "Used direct .odb extraction (heuristic). "
                "For best results use the relational CSV export (przepisy.csv + skladniki + produkty)."  # pylint: disable=line-too-long
            )

    # 4. Final fallback
    if not recipes:
        recipes = LEGACY_RECIPES

    logger.info("Seeding %d recipes from legacy data...", len(recipes))
    for r in recipes:
        create_recipe(r)

    logger.info("Legacy migration seed completed.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.isdir(arg):
            # python -m ... /path/to/dir-containing-the-csvs
            seed_from_legacy(
                base_dir=arg, odb_path=os.path.join(arg, "przepisy_tmp.odb")
            )
        elif arg.endswith(".csv"):
            seed_from_legacy(csv_path=arg)
        else:
            seed_from_legacy()
    else:
        seed_from_legacy()
