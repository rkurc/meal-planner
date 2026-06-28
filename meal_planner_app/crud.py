"""
CRUD (Create, Read, Update, Delete) operations for managing recipes and meal plans
using in-memory data structures. Also includes shopping list generation and recipe search.
"""

import uuid
from collections import defaultdict
from typing import List, Dict, Optional, Union
from .models.recipe import Recipe
from .models.ingredient import Ingredient
from .models.meal_plan import MealPlan
from .models.shopping_list import ShoppingList, ShoppingListItem

recipes_db: List[Recipe] = []


def create_recipe(
    name: str,
    instructions: str,
    ingredients_data: Optional[List[Dict[str, Union[str, float]]]] = None,
    description: Optional[str] = None,
    source_url: Optional[str] = None,
) -> Recipe:
    """
    Creates a new recipe and stores it in the in-memory database.
    ingredients_data should be a list of dicts like:
    [{'name': 'sugar', 'quantity': 1, 'unit': 'cup', 'location_id': '4'}]
    """
    parsed_ingredients = []
    if ingredients_data:
        for ing_data in ingredients_data:
            parsed_ingredients.append(
                Ingredient(
                    name=ing_data["name"],
                    quantity=ing_data["quantity"],
                    unit=ing_data["unit"],
                    location_id=ing_data.get("location_id"),
                    location=ing_data.get("location"),
                )
            )

    recipe = Recipe(
        name=name,
        description=description,
        ingredients=parsed_ingredients,
        instructions=instructions,
        source_url=source_url,
    )
    recipes_db.append(recipe)
    return recipe


def get_recipe(recipe_id: uuid.UUID) -> Optional[Recipe]:
    """Retrieves a recipe by its ID."""
    for recipe in recipes_db:
        if recipe.recipe_id == recipe_id:
            return recipe
    return None


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
        parsed_ingredients = []
        for ing_data in ingredients_data:
            parsed_ingredients.append(
                Ingredient(
                    name=ing_data["name"],
                    quantity=ing_data["quantity"],
                    unit=ing_data["unit"],
                    location_id=ing_data.get("location_id"),
                    location=ing_data.get("location"),
                )
            )
        recipe.ingredients = parsed_ingredients

    return recipe


def delete_recipe(recipe_id: uuid.UUID) -> bool:
    """Deletes a recipe by its ID."""
    recipe = get_recipe(recipe_id)
    if recipe:
        recipes_db.remove(recipe)
        return True
    return False


def list_recipes() -> List[Recipe]:
    """Returns all recipes."""
    return recipes_db


def list_unique_ingredient_names() -> List[str]:
    """Returns a sorted list of unique ingredient names present in all recipes."""
    names: set = set()
    for recipe in recipes_db:
        for ing in recipe.ingredients:
            if ing.name and ing.name.strip():
                names.add(ing.name.strip())
    return sorted(names)


def list_unique_locations() -> List[str]:
    """Returns a sorted list of unique location names (or ids) from ingredients."""
    locs: set = set()
    for recipe in recipes_db:
        for ing in recipe.ingredients:
            loc = getattr(ing, "location", None) or getattr(ing, "location_id", None)
            if loc and str(loc).strip():
                locs.add(str(loc).strip())
    return sorted(locs)


def reset_recipes_db():
    """Helper function to reset the database, primarily for testing."""
    # pylint: disable=global-statement
    global recipes_db
    recipes_db = []


# --- MealPlan CRUD Operations ---

meal_plans_db: List[MealPlan] = []


def reset_meal_plans_db():
    """Helper function to reset the meal plans database, primarily for testing."""
    # pylint: disable=global-statement
    global meal_plans_db
    meal_plans_db = []


def create_meal_plan(
    name: str,
    description: str = "",
    recipe_ids: Optional[List[uuid.UUID]] = None,
) -> MealPlan:
    """Creates a new meal plan."""
    if recipe_ids is None:
        recipe_ids = []
    meal_plan = MealPlan(name=name, description=description, recipe_ids=recipe_ids)
    meal_plans_db.append(meal_plan)
    return meal_plan


def get_meal_plan(meal_plan_id: uuid.UUID) -> Optional[MealPlan]:
    """Retrieves a meal plan by its ID."""
    for mp in meal_plans_db:
        if mp.meal_plan_id == meal_plan_id:
            return mp
    return None


def list_meal_plans() -> List[MealPlan]:
    """Returns all meal plans."""
    return meal_plans_db


def add_recipe_to_meal_plan(
    meal_plan_id: uuid.UUID, recipe_id: uuid.UUID
) -> Optional[MealPlan]:
    """Adds a recipe ID to a meal plan's recipe_ids list."""
    meal_plan = get_meal_plan(meal_plan_id)
    recipe = get_recipe(recipe_id)  # Check if recipe exists

    if not meal_plan:
        return None  # Meal plan not found
    if not recipe:
        # Depending on desired behavior, could raise error or just not add
        return meal_plan  # Or None, if we want to signify failure due to non-existent recipe

    if recipe_id not in meal_plan.recipe_ids:
        meal_plan.recipe_ids.append(recipe_id)
    return meal_plan


def remove_recipe_from_meal_plan(
    meal_plan_id: uuid.UUID, recipe_id: uuid.UUID
) -> Optional[MealPlan]:
    """Removes a recipe ID from a meal plan's recipe_ids list."""
    meal_plan = get_meal_plan(meal_plan_id)
    if not meal_plan:
        return None

    if recipe_id in meal_plan.recipe_ids:
        meal_plan.recipe_ids.remove(recipe_id)
    return meal_plan


def delete_meal_plan(meal_plan_id: uuid.UUID) -> bool:
    """Deletes a meal plan by its ID."""
    meal_plan = get_meal_plan(meal_plan_id)
    if meal_plan:
        meal_plans_db.remove(meal_plan)
        return True
    return False


def update_meal_plan(
    meal_plan_id: uuid.UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    recipe_ids: Optional[List[uuid.UUID]] = None,
) -> Optional[MealPlan]:
    """Updates an existing meal plan's name and/or recipe list."""
    meal_plan = get_meal_plan(meal_plan_id)
    if not meal_plan:
        return None

    if name is not None:
        meal_plan.name = name

    if description is not None:
        meal_plan.description = description

    if recipe_ids is not None:
        # Here we replace the entire list of recipe_ids
        meal_plan.recipe_ids = recipe_ids

    return meal_plan


# --- Shopping List Generation ---


# pylint: disable=too-many-locals,too-many-branches
def generate_shopping_list(
    meal_plan_id: uuid.UUID,
) -> Optional[Dict[str, List[Dict[str, Union[str, float, List[str]]]]]]:
    """
    Generates an aggregated shopping list for a given meal plan.
    Returns a dict grouped by location (from lokalizacje): {location_name: [items...], ...}
    or None if the meal plan is not found.
    Items without a location use key "".
    """
    meal_plan = get_meal_plan(meal_plan_id)
    if not meal_plan:
        return None

    aggregated_ingredients: Dict[str, Dict[str, Union[str, float, List[str]]]] = {}

    for recipe_id in meal_plan.recipe_ids:
        recipe = get_recipe(recipe_id)
        if not recipe:
            continue  # Skip if a recipe ID in the plan doesn't exist

        for ingredient in recipe.ingredients:
            loc = getattr(ingredient, "location", None) or ""
            ingredient_key = f"{ingredient.name}_{ingredient.unit}_{loc}"
            current_quantity_str = str(
                ingredient.quantity
            )  # Ensure it's a string for consistency first
            current_quantity_numeric: Optional[float] = None

            try:
                current_quantity_numeric = float(current_quantity_str)
            except (ValueError, TypeError):
                # Quantity is not a simple float (e.g., "to taste", "1-2", or empty)
                pass

            if ingredient_key in aggregated_ingredients:
                existing_entry = aggregated_ingredients[ingredient_key]
                existing_quantity = existing_entry["quantity"]

                if current_quantity_numeric is not None and isinstance(
                    existing_quantity, (int, float)
                ):
                    # Both are numeric, sum them
                    existing_entry["quantity"] = (
                        existing_quantity + current_quantity_numeric
                    )
                elif isinstance(existing_quantity, list):
                    # Existing is already a list, append new quantity string
                    existing_quantity.append(current_quantity_str)
                else:
                    # Existing was a single value (numeric or string), convert to list and add both
                    existing_entry["quantity"] = [
                        str(existing_quantity),
                        current_quantity_str,
                    ]
            else:
                # New ingredient for the shopping list
                aggregated_ingredients[ingredient_key] = {
                    "name": ingredient.name,
                    "quantity": (
                        current_quantity_numeric
                        if current_quantity_numeric is not None
                        else current_quantity_str
                    ),
                    "unit": ingredient.unit,
                    "location": getattr(ingredient, "location", None),
                    "location_id": getattr(ingredient, "location_id", None),
                }
                # If quantity was empty string and we tried to make it float, it would be None.
                # Ensure it's stored as original string if not numeric.
                if (
                    current_quantity_numeric is None
                    and aggregated_ingredients[ingredient_key]["quantity"] is None
                ):
                    aggregated_ingredients[ingredient_key][
                        "quantity"
                    ] = current_quantity_str

    # Group by location for easy grouping by lokalizacje (aisle/category)
    grouped: Dict[str, List[Dict[str, Union[str, float, List[str]]]]] = defaultdict(
        list
    )
    for item in aggregated_ingredients.values():
        loc = item.get("location") or ""
        grouped[loc].append(item)

    # Sort locations alphabetically, "Other"/empty last; sort items inside each group by name
    def _loc_key(l):
        return (l == "", l)  # empty/unknown at end

    result = {}
    for loc in sorted(grouped.keys(), key=_loc_key):
        items = sorted(grouped[loc], key=lambda x: str(x.get("name", "")))
        result[loc] = items

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

shopping_lists_db: List[ShoppingList] = []


def reset_shopping_lists_db():
    """Helper function to reset the shopping lists database, for testing."""
    # pylint: disable=global-statement
    global shopping_lists_db
    shopping_lists_db = []


def create_shopping_list(meal_plan_id: uuid.UUID) -> Optional[ShoppingList]:
    """
    Generates a shopping list from a meal plan and saves it to the database.
    """
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
    new_shopping_list = ShoppingList(
        name=f"Shopping List for {meal_plan.name}",
        items=list_items,
        meal_plan_id=meal_plan_id,
    )

    shopping_lists_db.append(new_shopping_list)
    return new_shopping_list


def get_shopping_list(shopping_list_id: uuid.UUID) -> Optional[ShoppingList]:
    """Retrieves a shopping list by its ID."""
    for sl in shopping_lists_db:
        if sl.id == shopping_list_id:
            return sl
    return None


def list_shopping_lists() -> List[ShoppingList]:
    """Returns all saved shopping lists."""
    return shopping_lists_db


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

    return shopping_list


def delete_shopping_list(shopping_list_id: uuid.UUID) -> bool:
    """Deletes a shopping list by its ID."""
    shopping_list = get_shopping_list(shopping_list_id)
    if shopping_list:
        shopping_lists_db.remove(shopping_list)
        return True
    return False


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

        for recipe in recipes_db:
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
