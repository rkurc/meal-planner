"""Meal plan CRUD. Persistence goes through MealPlannerDao."""

import uuid
from typing import List, Dict, Optional, Any

from meal_planner_app.domain._dao import get_dao
from meal_planner_app.domain.recipes import get_recipe
from meal_planner_app.models.meal_plan import MealPlan, _normalize_recipe_entries


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

    if not meal_plan or not recipe:
        return None

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
