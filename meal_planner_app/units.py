"""Compatible-unit conversion for shopping-list consolidation.

Rules (kept in sync with tests in test_units.py / test_shopping_list.py):

- Mass family: g, gram(s), kg, kilogram(s). Case-insensitive; surrounding
  whitespace is ignored.
- Volume family: ml, millilitre(s)/milliliter(s), l, litre(s)/liter(s).
- Never convert across families (g ↛ ml) or to unrelated units (apples ↛ g).
- Quantities are summed in base units (grams or millilitres). Display unit:
  * If every contributing unit is the same scale (all g, or all kg), keep
    that scale using the canonical short form (g/kg/ml/l).
  * If scales are mixed, prefer the larger unit when the total is >= 1000
    base units (1000g → kg, 1000ml → l); otherwise keep the smaller unit.
- Aggregation identity is (name, unit-family-or-raw-unit, location) so the
  same ingredient in two aisles stays on two lines.
"""

from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

MASS = "mass"
VOLUME = "volume"
LARGE_UNIT_THRESHOLD = 1000.0

# Canonical short forms for each scale.
GRAM = "g"
KILOGRAM = "kg"
MILLILITRE = "ml"
LITRE = "l"

# normalized unit -> (family, multiplier to base units, canonical scale)
_UNIT_TABLE = {
    "g": (MASS, 1.0, GRAM),
    "gram": (MASS, 1.0, GRAM),
    "grams": (MASS, 1.0, GRAM),
    "kg": (MASS, 1000.0, KILOGRAM),
    "kilogram": (MASS, 1000.0, KILOGRAM),
    "kilograms": (MASS, 1000.0, KILOGRAM),
    "ml": (VOLUME, 1.0, MILLILITRE),
    "millilitre": (VOLUME, 1.0, MILLILITRE),
    "milliliter": (VOLUME, 1.0, MILLILITRE),
    "millilitres": (VOLUME, 1.0, MILLILITRE),
    "milliliters": (VOLUME, 1.0, MILLILITRE),
    "l": (VOLUME, 1000.0, LITRE),
    "litre": (VOLUME, 1000.0, LITRE),
    "liter": (VOLUME, 1000.0, LITRE),
    "litres": (VOLUME, 1000.0, LITRE),
    "liters": (VOLUME, 1000.0, LITRE),
}

_LARGE_SCALE = {MASS: KILOGRAM, VOLUME: LITRE}
_SMALL_SCALE = {MASS: GRAM, VOLUME: MILLILITRE}

QuantityValue = Union[float, str, List[Union[str, float]]]


def normalize_unit(unit: Optional[str]) -> str:
    """Trim and lowercase a unit string. None/blank → empty string."""
    if unit is None:
        return ""
    return str(unit).strip().lower()


def unit_family(unit: Optional[str]) -> Optional[str]:
    """Return MASS, VOLUME, or None if the unit is not convertible."""
    info = _UNIT_TABLE.get(normalize_unit(unit))
    if info is None:
        return None
    return info[0]


def aggregation_unit_key(unit: Optional[str]) -> str:
    """Key fragment so g and kg share an identity; cups stay 'cup'."""
    family = unit_family(unit)
    if family:
        return family
    return normalize_unit(unit)


def aggregation_key(name: str, unit: Optional[str], location: Optional[str]) -> str:
    """Identity for one shopping-list line: name + compatible unit + aisle."""
    loc = location or ""
    return f"{name}_{aggregation_unit_key(unit)}_{loc}"


def _as_float(quantity: Union[str, float, int, None]) -> Optional[float]:
    try:
        return float(quantity)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _pretty_qty(qty: float) -> float:
    """Round out binary-float noise; keep integers looking like integers."""
    rounded = round(float(qty), 10)
    nearest = round(rounded)
    if abs(rounded - nearest) < 1e-9:
        return float(nearest)
    return rounded


def to_base_quantity(
    quantity: float, unit: Optional[str]
) -> Optional[Tuple[float, str, str]]:
    """Convert qty to (base_qty, family, canonical_scale), or None."""
    info = _UNIT_TABLE.get(normalize_unit(unit))
    if info is None:
        return None
    family, multiplier, scale = info
    return quantity * multiplier, family, scale


def choose_display_unit(
    base_qty: float, family: str, scales: Iterable[str]
) -> Tuple[float, str]:
    """Pick display (qty, unit) from a base total and the scales that fed it."""
    unique = {scale for scale in scales if scale}
    large = _LARGE_SCALE[family]
    small = _SMALL_SCALE[family]
    if len(unique) == 1:
        scale = next(iter(unique))
    elif base_qty >= LARGE_UNIT_THRESHOLD:
        scale = large
    else:
        scale = small
    if scale == large:
        return _pretty_qty(base_qty / LARGE_UNIT_THRESHOLD), large
    return _pretty_qty(base_qty), small


def consolidate_numeric(
    pairs: Sequence[Tuple[float, str]],
) -> Optional[Tuple[float, str]]:
    """Merge numeric (qty, unit) pairs in one family.

    Returns (quantity, canonical_unit) or None if empty / incompatible.
    """
    if not pairs:
        return None
    family: Optional[str] = None
    total = 0.0
    scales: List[str] = []
    for qty, unit in pairs:
        converted = to_base_quantity(float(qty), unit)
        if converted is None:
            return None
        base, fam, scale = converted
        if family is None:
            family = fam
        elif fam != family:
            return None
        total += base
        scales.append(scale)
    assert family is not None  # pairs non-empty and all converted
    return choose_display_unit(total, family, scales)


def add_to_aggregate(
    aggregated: Dict[str, dict],
    item: dict,
    count: float = 1.0,
) -> None:
    """Accumulate one recipe-line into a name/family/location bucket.

    ``item`` keys: name, quantity, unit, location, location_id.
    Numeric quantities are multiplied by ``count`` (recipe servings).
    """
    name = item.get("name") or ""
    unit = item.get("unit") or ""
    location = item.get("location")
    location_id = item.get("location_id")
    raw_quantity = item.get("quantity")
    numeric = _as_float(raw_quantity)
    if numeric is not None:
        numeric = numeric * float(count)
        stored_quantity: Union[float, str] = numeric
    else:
        stored_quantity = "" if raw_quantity is None else str(raw_quantity)

    key = aggregation_key(name, unit, location)
    contribution = {
        "numeric": numeric,
        "unit": unit,
        "quantity": stored_quantity,
    }
    if key not in aggregated:
        aggregated[key] = {
            "name": name,
            "location": location,
            "location_id": location_id,
            "contributions": [contribution],
        }
        return
    aggregated[key]["contributions"].append(contribution)
    # Prefer a resolved location string if a later line supplies one.
    if location and not aggregated[key].get("location"):
        aggregated[key]["location"] = location
    if location_id and not aggregated[key].get("location_id"):
        aggregated[key]["location_id"] = location_id


def _item_dict(
    name: str,
    quantity: QuantityValue,
    unit: str,
    location: Optional[str],
    location_id: Optional[str],
) -> dict:
    return {
        "name": name,
        "quantity": quantity,
        "unit": unit,
        "location": location,
        "location_id": location_id,
    }


def _finalize_entry(entry: dict) -> dict:
    contribs: List[dict] = entry["contributions"]
    name = entry["name"]
    location = entry.get("location")
    location_id = entry.get("location_id")
    if not contribs:
        return _item_dict(name, "", "", location, location_id)

    all_numeric = all(c["numeric"] is not None for c in contribs)
    if all_numeric:
        pairs = [(c["numeric"], c["unit"]) for c in contribs]
        consolidated = consolidate_numeric(pairs)
        if consolidated is not None:
            qty, unit = consolidated
        else:
            qty = _pretty_qty(sum(c["numeric"] for c in contribs))
            unit = contribs[0]["unit"]
        return _item_dict(name, qty, unit, location, location_id)

    if len(contribs) == 1:
        only = contribs[0]
        return _item_dict(name, only["quantity"], only["unit"], location, location_id)

    qty_list: List[Union[str, float]] = [
        str(c["numeric"]) if c["numeric"] is not None else str(c["quantity"])
        for c in contribs
    ]
    return _item_dict(name, qty_list, contribs[0]["unit"], location, location_id)


def finalize_aggregated(aggregated: Dict[str, dict]) -> List[dict]:
    """Turn accumulator buckets into shopping-list item dicts."""
    return [_finalize_entry(entry) for entry in aggregated.values()]
