"""Recipe CRUD and search. Persistence goes through MealPlannerDao."""

import uuid
from typing import List, Dict, Optional, Union

from meal_planner_app.domain._dao import get_dao
from meal_planner_app.models.ingredient import Ingredient, MasterIngredient
from meal_planner_app.models.recipe import Recipe


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


def reset_recipes_db():
    """Delete all recipes then catalog ingredients. For tests / E2E seed."""
    dao = get_dao()
    for recipe in list(dao.recipes.find_all()):
        dao.recipes.delete(recipe.recipe_id)
    for ingredient in list(dao.ingredients.find_all()):
        dao.ingredients.delete(ingredient.ingredient_id)


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
