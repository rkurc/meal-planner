"""Shopping list generation, grouping, and persistence."""

import uuid
from collections import defaultdict
from typing import List, Dict, Optional, Union

from meal_planner_app.domain._dao import get_dao
from meal_planner_app.domain.meal_plans import get_meal_plan
from meal_planner_app.domain.recipes import get_recipe
from meal_planner_app.models.meal_plan import _normalize_recipe_entries
from meal_planner_app.models.shopping_list import ShoppingList, ShoppingListItem
from meal_planner_app.units import add_to_aggregate, finalize_aggregated


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
                recipe_name=recipe.name or "",
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
                source_recipe_names=list(item.get("source_recipe_names") or []),
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
        updated_items = [
            ShoppingListItem(
                name=item_data.get("name", ""),
                quantity=item_data.get("quantity", ""),
                unit=item_data.get("unit") or "",
                purchased=bool(item_data.get("purchased", False)),
                location=item_data.get("location"),
                location_id=(
                    str(item_data["location_id"])
                    if item_data.get("location_id") is not None
                    else None
                ),
                source_recipe_names=list(item_data.get("source_recipe_names") or []),
            )
            for item_data in items
        ]
        shopping_list.items = updated_items

    return get_dao().shopping_lists.update(shopping_list)


def delete_shopping_list(shopping_list_id: uuid.UUID) -> bool:
    """Deletes a shopping list by its ID."""
    return get_dao().shopping_lists.delete(shopping_list_id)
