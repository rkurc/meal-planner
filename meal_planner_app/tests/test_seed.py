"""E2E/dev seed isolation: seed_database must wipe all aggregates."""

from meal_planner_app import crud
from meal_planner_app.seed_db import RECIPES_TO_SEED, seed_database, seed_if_empty


def _weekly():
    plans = crud.list_meal_plans()
    return next((p for p in plans if p.name == "Weekly Meal Plan"), None)


def test_seed_database_twice_keeps_recipes_on_weekly_plan():
    seed_database()
    crud.create_shopping_list(name="orphan")
    seed_database()

    recipes = crud.list_recipes()
    assert len(recipes) == len(RECIPES_TO_SEED)
    names = {r.name for r in recipes}
    assert names == {r["name"] for r in RECIPES_TO_SEED}

    weekly = _weekly()
    assert weekly is not None
    assert len(weekly.recipes) == len(RECIPES_TO_SEED)
    seeded_ids = {r.recipe_id for r in recipes}
    plan_ids = {e["recipe_id"] for e in weekly.recipes}
    assert plan_ids == seeded_ids

    assert crud.list_shopping_lists() == []
    assert len(crud.list_meal_plans()) == 1


def test_seed_if_empty_does_not_wipe_existing_recipes():
    seed_if_empty()
    extra = crud.create_recipe(name="User Recipe", instructions="Keep me.")
    seed_if_empty()
    names = {r.name for r in crud.list_recipes()}
    assert extra.name in names
    assert "Classic Pancakes" in names
