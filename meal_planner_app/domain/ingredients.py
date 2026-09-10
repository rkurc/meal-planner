"""Master ingredient CRUD, catalog summaries, and usage lookups."""

import uuid
from collections import defaultdict
from typing import List, Dict, Optional, Union

from meal_planner_app.domain._dao import get_dao
from meal_planner_app.domain.recipes import list_recipes
from meal_planner_app.models.ingredient import MasterIngredient
from meal_planner_app.models.recipe import Recipe


def list_unique_ingredient_names() -> List[str]:
    """Returns a sorted list of unique catalog ingredient names."""
    return [
        ing.name.strip()
        for ing in get_dao().ingredients.find_all()
        if ing.name and ing.name.strip()
    ]


def list_unique_locations() -> List[str]:
    """Returns a sorted list of unique location names (or ids) from the catalog."""
    locs: set = set()
    for ing in get_dao().ingredients.find_all():
        loc = ing.location or ing.location_id
        if loc and str(loc).strip():
            locs.add(str(loc).strip())
    return sorted(locs)


def list_unique_units() -> List[str]:
    """Unique non-empty units from recipe lines and catalog defaults."""
    units: set = set()
    for ing in get_dao().ingredients.find_all():
        if ing.default_unit and str(ing.default_unit).strip():
            units.add(str(ing.default_unit).strip())
    for recipe in list_recipes():
        for line in recipe.ingredients:
            if line.unit and str(line.unit).strip():
                units.add(str(line.unit).strip())
    return sorted(units)


def get_recipes_for_ingredient(name: str) -> List[Recipe]:
    """Return recipes containing an ingredient with the exact (trimmed, case-insensitive) name.
    Used for IngredientDetail view. Pure read aggregation, does not modify any data.
    """
    if not name or not name.strip():
        return []
    normalized = name.strip().lower()
    matching = []
    for recipe in list_recipes():
        for ing in recipe.ingredients:
            if ing.name and ing.name.strip().lower() == normalized:
                matching.append(recipe)
                break
    return matching


def list_ingredients_summary() -> List[Dict[str, Union[str, int, Optional[str]]]]:
    """Return sorted catalog summaries: {id, name, usage_count, unit, location}."""
    usage: Dict[uuid.UUID, int] = defaultdict(int)
    for recipe in list_recipes():
        for ing in recipe.ingredients:
            if ing.ingredient_id:
                usage[ing.ingredient_id] += 1
    summaries: List[Dict[str, Union[str, int, Optional[str]]]] = []
    for master in get_dao().ingredients.find_all():
        summaries.append(
            {
                "id": str(master.ingredient_id),
                "name": master.name,
                "usage_count": usage.get(master.ingredient_id, 0),
                "unit": master.default_unit or "",
                "location": master.location or master.location_id or "",
            }
        )
    return sorted(summaries, key=lambda x: str(x["name"]).lower())


class DuplicateIngredientNameError(ValueError):
    """Raised when a catalog ingredient name is already taken."""


class IngredientInUseError(Exception):
    """Raised when delete is blocked because recipes still reference the row."""

    def __init__(self, usage_count: int):
        super().__init__("Ingredient is still used by recipes")
        self.usage_count = usage_count


def get_master_ingredient(ingredient_id: uuid.UUID) -> Optional[MasterIngredient]:
    """Return a catalog ingredient by id, or None."""
    return get_dao().ingredients.find_by_id(ingredient_id)


def get_master_ingredient_by_name(name: str) -> Optional[MasterIngredient]:
    """Return a catalog ingredient by trimmed name, or None."""
    stripped = (name or "").strip()
    if not stripped:
        return None
    return get_dao().ingredients.find_by_name(stripped)


def create_master_ingredient(
    name: str,
    default_unit: str = "",
    location: Optional[str] = None,
    location_id: Optional[Union[str, int]] = None,
) -> MasterIngredient:
    """Insert a catalog ingredient. Name is trimmed and must be unique."""
    stripped = (name or "").strip()
    if not stripped:
        raise ValueError("name is required")
    dao = get_dao()
    if dao.ingredients.find_by_name(stripped):
        raise DuplicateIngredientNameError("Ingredient name already exists.")
    location_id_str = None if location_id is None else str(location_id).strip() or None
    location_str = location.strip() if isinstance(location, str) else location
    if location_str == "":
        location_str = None
    master = MasterIngredient(
        name=stripped,
        default_unit=(default_unit or "").strip() if default_unit is not None else "",
        location=location_str,
        location_id=location_id_str,
    )
    return dao.ingredients.insert(master)


def update_master_ingredient(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ingredient_id: uuid.UUID,
    name: Optional[str] = None,
    default_unit: Optional[str] = None,
    location: Optional[str] = None,
    location_id: Optional[Union[str, int]] = None,
) -> Optional[MasterIngredient]:
    """Update a catalog ingredient by id. Unique name is still enforced."""
    dao = get_dao()
    existing = dao.ingredients.find_by_id(ingredient_id)
    if not existing:
        return None
    if name is not None:
        stripped = name.strip()
        if not stripped:
            raise ValueError("name is required")
        other = dao.ingredients.find_by_name(stripped)
        if other and other.ingredient_id != existing.ingredient_id:
            raise DuplicateIngredientNameError("Ingredient name already exists.")
        existing.name = stripped
    if default_unit is not None:
        existing.default_unit = (
            default_unit.strip() if isinstance(default_unit, str) else str(default_unit)
        )
    if location is not None:
        existing.location = location.strip() if isinstance(location, str) else location
        if existing.location == "":
            existing.location = None
    if location_id is not None:
        existing.location_id = str(location_id).strip() or None
    return dao.ingredients.update(existing)


def delete_master_ingredient(ingredient_id: uuid.UUID) -> bool:
    """Delete a catalog ingredient.

    Returns True if deleted. Raises IngredientInUseError when recipes still
    reference the row (ON DELETE RESTRICT). Returns False if the id is missing.
    """
    dao = get_dao()
    existing = dao.ingredients.find_by_id(ingredient_id)
    if existing is None:
        return False
    if dao.ingredients.delete(ingredient_id):
        return True
    raise IngredientInUseError(len(get_recipes_for_ingredient(existing.name)))
