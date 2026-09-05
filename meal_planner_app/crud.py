"""
Application operations for recipes, meal plans, and shopping lists.
Persistence goes through MealPlannerDao (see dao/). Search and shopping
aggregation stay here and never execute SQL.
"""

import uuid
from collections import defaultdict
from typing import List, Dict, Optional, Union, Any

from meal_planner_app.dao.factory import create_dao
from meal_planner_app.dao.protocol import MealPlannerDao
from meal_planner_app.units import add_to_aggregate, finalize_aggregated
from .models.recipe import Recipe
from .models.ingredient import Ingredient, MasterIngredient
from .models.meal_plan import MealPlan, _normalize_recipe_entries
from .models.shopping_list import ShoppingList, ShoppingListItem

_dao: Optional[MealPlannerDao] = None


def set_dao(dao: Optional[MealPlannerDao]) -> None:
    """Install (or clear) the process-wide DAO. Tests pass an in-memory instance."""
    # pylint: disable=global-statement
    global _dao
    _dao = dao


def get_dao() -> MealPlannerDao:
    """Lazy default: MEAL_PLANNER_DB or data/meal_planner.db."""
    # pylint: disable=global-statement
    global _dao
    if _dao is None:
        _dao = create_dao()
    return _dao


def _ensure_master_ingredient(
    name: str,
    unit: str = "",
    location: Optional[str] = None,
    location_id: Optional[Union[str, int]] = None,
) -> MasterIngredient:
    """Get-or-create a catalog row by stripped name. Does not overwrite set defaults."""
    dao = get_dao()
    stripped = (name or "").strip()
    location_id_str = None if location_id is None else str(location_id)
    existing = dao.ingredients.find_by_name(stripped) if stripped else None
    if existing:
        changed = False
        if not existing.default_unit and unit:
            existing.default_unit = unit
            changed = True
        if not existing.location and location:
            existing.location = location
            changed = True
        if not existing.location_id and location_id_str:
            existing.location_id = location_id_str
            changed = True
        if changed:
            dao.ingredients.update(existing)
        return existing
    master = MasterIngredient(
        name=stripped or name,
        default_unit=unit or "",
        location=location,
        location_id=location_id_str,
    )
    return dao.ingredients.insert(master)


def _lines_from_data(
    ingredients_data: Optional[List[Dict[str, Union[str, float]]]],
) -> List[Ingredient]:
    lines: List[Ingredient] = []
    if not ingredients_data:
        return lines
    for ing_data in ingredients_data:
        unit = ing_data.get("unit") or ""
        master = _ensure_master_ingredient(
            name=str(ing_data["name"]),
            unit=str(unit),
            location=ing_data.get("location"),  # type: ignore[arg-type]
            location_id=ing_data.get("location_id"),
        )
        line_location = ing_data.get("location")
        line_location_id = ing_data.get("location_id")
        lines.append(
            Ingredient(
                name=master.name,
                quantity=ing_data["quantity"],
                unit=str(unit),
                location_id=(
                    str(line_location_id)
                    if line_location_id is not None
                    else master.location_id
                ),
                location=(
                    str(line_location) if line_location is not None else master.location
                ),
                ingredient_id=master.ingredient_id,
            )
        )
    return lines


def create_recipe(
    name: str,
    instructions: str,
    ingredients_data: Optional[List[Dict[str, Union[str, float]]]] = None,
    description: Optional[str] = None,
    source_url: Optional[str] = None,
) -> Recipe:
    """
    Creates a new recipe and persists it.
    ingredients_data should be a list of dicts like:
    [{'name': 'sugar', 'quantity': 1, 'unit': 'cup', 'location_id': '4'}]
    """
    recipe = Recipe(
        name=name,
        description=description,
        ingredients=_lines_from_data(ingredients_data),
        instructions=instructions,
        source_url=source_url,
    )
    return get_dao().recipes.insert(recipe)


def get_recipe(recipe_id: uuid.UUID) -> Optional[Recipe]:
    """Retrieves a recipe by its ID."""
    return get_dao().recipes.find_by_id(recipe_id)


def update_recipe(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    recipe_id: uuid.UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    ingredients_data: Optional[List[Dict[str, Union[str, float]]]] = None,
    instructions: Optional[str] = None,
    source_url: Optional[str] = None,
) -> Optional[Recipe]:
    """Updates an existing recipe."""
    recipe = get_recipe(recipe_id)
    if not recipe:
        return None

    if name is not None:
        recipe.name = name
    if description is not None:
        recipe.description = description
    if instructions is not None:
        recipe.instructions = instructions
    if source_url is not None:
        recipe.source_url = source_url

    if ingredients_data is not None:
        recipe.ingredients = _lines_from_data(ingredients_data)

    return get_dao().recipes.update(recipe)


def delete_recipe(recipe_id: uuid.UUID) -> bool:
    """Deletes a recipe by its ID."""
    return get_dao().recipes.delete(recipe_id)


def list_recipes() -> List[Recipe]:
    """Returns all recipes."""
    return get_dao().recipes.find_all()


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


def reset_recipes_db():
    """Delete all recipes then catalog ingredients. For tests / E2E seed."""
    dao = get_dao()
    for recipe in list(dao.recipes.find_all()):
        dao.recipes.delete(recipe.recipe_id)
    for ingredient in list(dao.ingredients.find_all()):
        dao.ingredients.delete(ingredient.ingredient_id)


# --- MealPlan CRUD Operations ---


def reset_meal_plans_db():
    """Delete all meal plans. For tests."""
    dao = get_dao()
    for meal_plan in list(dao.meal_plans.find_all()):
        dao.meal_plans.delete(meal_plan.meal_plan_id)


def create_meal_plan(
    name: str,
    description: str = "",
    recipe_ids: Optional[List[uuid.UUID]] = None,
    recipes: Optional[List[Dict[str, Any]]] = None,
) -> MealPlan:
    """Creates a new meal plan.
    Accepts legacy recipe_ids or new recipes list with counts (fractions ok).
    """
    if recipes is None and recipe_ids is not None:
        recipes = _normalize_recipe_entries(
            [{"recipe_id": rid, "count": 1.0} for rid in recipe_ids]
        )
    recipes = _normalize_recipe_entries(recipes)
    meal_plan = MealPlan(name=name, description=description, recipes=recipes)
    return get_dao().meal_plans.insert(meal_plan)


def get_meal_plan(meal_plan_id: uuid.UUID) -> Optional[MealPlan]:
    """Retrieves a meal plan by its ID."""
    return get_dao().meal_plans.find_by_id(meal_plan_id)


def list_meal_plans() -> List[MealPlan]:
    """Returns all meal plans."""
    return get_dao().meal_plans.find_all()


def add_recipe_to_meal_plan(
    meal_plan_id: uuid.UUID, recipe_id: uuid.UUID, count: float = 1.0
) -> Optional[MealPlan]:
    """Adds a recipe to a meal plan (or increases count if already present).
    Defaults to count=1 for legacy callers.
    """
    meal_plan = get_meal_plan(meal_plan_id)
    recipe = get_recipe(recipe_id)  # Check if recipe exists

    if not meal_plan:
        return None  # Meal plan not found
    if not recipe:
        # Depending on desired behavior, could raise error or just not add
        return meal_plan  # Or None, if we want to signify failure due to non-existent recipe

    existing = next((e for e in meal_plan.recipes if e["recipe_id"] == recipe_id), None)
    cnt = float(count)
    if existing:
        existing["count"] = float(existing.get("count", 1.0)) + cnt
    else:
        meal_plan.recipes.append({"recipe_id": recipe_id, "count": cnt})
    return get_dao().meal_plans.update(meal_plan)


def remove_recipe_from_meal_plan(
    meal_plan_id: uuid.UUID, recipe_id: uuid.UUID
) -> Optional[MealPlan]:
    """Removes a recipe from a meal plan (by id, regardless of count)."""
    meal_plan = get_meal_plan(meal_plan_id)
    if not meal_plan:
        return None

    meal_plan.recipes = [e for e in meal_plan.recipes if e["recipe_id"] != recipe_id]
    return get_dao().meal_plans.update(meal_plan)


def delete_meal_plan(meal_plan_id: uuid.UUID) -> bool:
    """Deletes a meal plan by its ID."""
    return get_dao().meal_plans.delete(meal_plan_id)


def update_meal_plan(
    meal_plan_id: uuid.UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    recipe_ids: Optional[List[uuid.UUID]] = None,
    recipes: Optional[List[Dict[str, Any]]] = None,
) -> Optional[MealPlan]:
    """Updates an existing meal plan's name and/or recipe list (with counts).
    Prefers 'recipes' arg if provided (new structure); falls back to recipe_ids for legacy.
    """
    meal_plan = get_meal_plan(meal_plan_id)
    if not meal_plan:
        return None

    if name is not None:
        meal_plan.name = name

    if description is not None:
        meal_plan.description = description

    if recipes is not None or recipe_ids is not None:
        meal_plan.recipes = _normalize_recipe_entries(recipes or recipe_ids or [])

    return get_dao().meal_plans.update(meal_plan)


# --- Shopping List Generation ---


def generate_shopping_list(
    meal_plan_id: uuid.UUID,
) -> Optional[Dict[str, List[Dict[str, Union[str, float, List[str]]]]]]:
    """
    Generates an aggregated shopping list for a given meal plan.
    Returns a dict grouped by location (from lokalizacje): {location_name: [items...], ...}
    or None if the meal plan is not found.
    Items without a location use key "".

    Compatible units (g↔kg, ml↔l and spellings) are consolidated at generation
    time; see meal_planner_app.units.
    """
    meal_plan = get_meal_plan(meal_plan_id)
    if not meal_plan:
        return None

    aggregated: Dict[str, dict] = {}

    recipe_entries = _normalize_recipe_entries(
        getattr(meal_plan, "recipes", None) or getattr(meal_plan, "recipe_ids", None)
    )

    for entry in recipe_entries:
        if isinstance(entry, dict):
            recipe_id = entry.get("recipe_id") or entry.get("id")
            count = float(entry.get("count", 1.0))
        else:
            recipe_id = entry
            count = 1.0
        recipe = get_recipe(recipe_id)
        if not recipe:
            continue  # Skip if a recipe ID in the plan doesn't exist

        for ingredient in recipe.ingredients:
            add_to_aggregate(
                aggregated,
                {
                    "name": ingredient.name,
                    "quantity": ingredient.quantity,
                    "unit": ingredient.unit,
                    "location": getattr(ingredient, "location", None),
                    "location_id": getattr(ingredient, "location_id", None),
                },
                count,
            )

    return _group_generated_items(finalize_aggregated(aggregated))


def _group_generated_items(
    items: List[Dict[str, Union[str, float, List[str]]]],
) -> Dict[str, List[Dict[str, Union[str, float, List[str]]]]]:
    """Group generated items by location; empty/missing last, names alpha inside."""
    grouped: Dict[str, List[Dict[str, Union[str, float, List[str]]]]] = defaultdict(
        list
    )
    for item in items:
        loc = item.get("location") or ""
        grouped[loc].append(item)

    def _loc_key(location: str):
        return (location == "", location)

    result: Dict[str, List[Dict[str, Union[str, float, List[str]]]]] = {}
    for loc in sorted(grouped.keys(), key=_loc_key):
        result[loc] = sorted(grouped[loc], key=lambda x: str(x.get("name", "")))
    return result


def _resolve_item_location(item: ShoppingListItem) -> str:
    """Return a location key for grouping.
    Prefers the resolved 'location' string, falls back to 'location_id'.
    Matches the rule used by list_unique_locations.
    """
    loc = item.location or item.location_id or ""
    return str(loc).strip()


def _group_items_for_pdf(
    items: List[ShoppingListItem], *, exclude_purchased: bool = False
) -> Dict[str, List[dict]]:
    """Group shopping list items by location for PDF rendering.
    Replicates the sort semantics from generate_shopping_list:
    locations sorted alpha with empty last; items sorted alpha by name within groups.
    """
    grouped: Dict[str, List[dict]] = defaultdict(list)
    for item in items:
        if exclude_purchased and item.purchased:
            continue
        loc_key = _resolve_item_location(item)
        item_dict = {
            "name": item.name,
            "quantity": item.quantity,
            "unit": item.unit,
            "location": item.location,
            "location_id": item.location_id,
        }
        grouped[loc_key].append(item_dict)

    def _loc_key(l: str):
        return (l == "", l)

    result: Dict[str, List[dict]] = {}
    for loc in sorted(grouped.keys(), key=_loc_key):
        sorted_items = sorted(grouped[loc], key=lambda x: str(x.get("name", "")))
        result[loc] = sorted_items
    return result


def shopping_list_to_pdf_data(
    shopping_list: ShoppingList,
) -> Dict[str, List[dict]]:
    """Public entry point: convert persisted ShoppingList to grouped PDF data.
    Excludes purchased items so the PDF is the 'to buy' list.
    """
    return _group_items_for_pdf(shopping_list.items, exclude_purchased=True)


# --- Shopping List CRUD Operations ---


def reset_shopping_lists_db():
    """Delete all shopping lists. For tests."""
    dao = get_dao()
    for shopping_list in list(dao.shopping_lists.find_all()):
        dao.shopping_lists.delete(shopping_list.id)


def create_shopping_list(
    meal_plan_id: Optional[uuid.UUID] = None, name: Optional[str] = None
) -> Optional[ShoppingList]:
    """
    Creates a shopping list.
    - If meal_plan_id is provided: generates from the meal plan (original behavior).
    - If no meal_plan_id: creates a standalone empty list with the given name (or default).
    """
    if meal_plan_id:
        meal_plan = get_meal_plan(meal_plan_id)
        if not meal_plan:
            return None

        # Use the existing generator function
        generated = generate_shopping_list(meal_plan_id)
        if generated is None:
            return None  # Should not happen if meal_plan exists

        # generated is now grouped {loc: [items...]} ; flatten for persisted ShoppingList
        if isinstance(generated, dict):
            flat = []
            for loc_items in generated.values():
                flat.extend(loc_items)
            generated_items = flat
        else:
            generated_items = generated or []

        # Convert generated items (dicts) to ShoppingListItem objects
        list_items = [
            ShoppingListItem(
                name=item["name"],
                quantity=item["quantity"],
                unit=item["unit"],
                purchased=False,  # Default to not purchased
                location=item.get("location"),
                location_id=item.get("location_id"),
            )
            for item in generated_items
        ]

        # Create the new shopping list object
        list_name = name or f"Shopping List for {meal_plan.name}"
        new_shopping_list = ShoppingList(
            name=list_name,
            items=list_items,
            meal_plan_id=meal_plan_id,
        )
    else:
        # Standalone empty list (for "a new list")
        list_name = name or "New Shopping List"
        new_shopping_list = ShoppingList(
            name=list_name,
            items=[],
            meal_plan_id=None,
        )

    return get_dao().shopping_lists.insert(new_shopping_list)


def get_shopping_list(shopping_list_id: uuid.UUID) -> Optional[ShoppingList]:
    """Retrieves a shopping list by its ID."""
    return get_dao().shopping_lists.find_by_id(shopping_list_id)


def list_shopping_lists() -> List[ShoppingList]:
    """Returns all saved shopping lists."""
    return get_dao().shopping_lists.find_all()


def update_shopping_list(
    shopping_list_id: uuid.UUID,
    name: Optional[str] = None,
    items: Optional[List[Dict]] = None,
) -> Optional[ShoppingList]:
    """
    Updates a shopping list's name and/or its items.
    'items' should be a list of dictionaries representing ShoppingListItem objects.
    """
    shopping_list = get_shopping_list(shopping_list_id)
    if not shopping_list:
        return None

    if name is not None:
        shopping_list.name = name

    if items is not None:
        # Re-create the list of ShoppingListItem objects from the provided dicts
        updated_items = [ShoppingListItem(**item_data) for item_data in items]
        shopping_list.items = updated_items

    return get_dao().shopping_lists.update(shopping_list)


def delete_shopping_list(shopping_list_id: uuid.UUID) -> bool:
    """Deletes a shopping list by its ID."""
    return get_dao().shopping_lists.delete(shopping_list_id)


# --- Recipe Search ---


def search_recipes(  # pylint: disable=too-many-branches
    query: str, filter_ingredient: Optional[str] = None
) -> List[Recipe]:
    """
    Searches for recipes based on a query string and optionally filters by an ingredient.
    The query is matched against recipe name, description, and ingredient names.
    If filter_ingredient is provided, results are further filtered to include only
    recipes containing that ingredient.
    Returns a list of unique matching Recipe objects.
    """
    base_recipes = []
    if query and query.strip() != "":
        normalized_query = query.lower().strip()
        matching_recipes_ids = set()

        for recipe in list_recipes():
            # Check name
            if normalized_query in recipe.name.lower():
                matching_recipes_ids.add(recipe.recipe_id)
                continue

            # Check description
            if recipe.description and normalized_query in recipe.description.lower():
                matching_recipes_ids.add(recipe.recipe_id)
                continue

            # Check ingredients for the main query
            for ingredient in recipe.ingredients:
                if normalized_query in ingredient.name.lower():
                    matching_recipes_ids.add(recipe.recipe_id)
                    break

        for recipe_id in matching_recipes_ids:
            recipe = get_recipe(recipe_id)
            if recipe:
                base_recipes.append(recipe)
    elif not filter_ingredient or filter_ingredient.strip() == "":
        # If no query and no filter_ingredient, return empty or all based on desired behavior.
        # Current: return empty if both are effectively empty.
        # If query is empty but filter_ingredient is present, we'll use all recipes as base.
        return []
    else:  # No query, but there IS a filter_ingredient
        base_recipes = list_recipes()

    if not filter_ingredient or filter_ingredient.strip() == "":
        return base_recipes  # No ingredient filter to apply

    normalized_filter_ingredient = filter_ingredient.lower().strip()
    filtered_results = []

    for recipe in base_recipes:
        for ingredient_obj in recipe.ingredients:
            if normalized_filter_ingredient in ingredient_obj.name.lower():
                filtered_results.append(recipe)
                break  # Found matching ingredient in this recipe, move to next recipe

    return filtered_results


# --- Ingredient views (catalog + usage from recipe links) ---


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
