"""
A script to seed the in-memory database with some initial data.
This is useful for development and for running end-to-end tests.

The RECIPES_TO_SEED list is the single source of truth for the data
used by the E2E tests (see frontend/e2e/main.spec.js) and the
test-only /api/test/seed-db endpoint.
"""

from meal_planner_app.crud import (
    create_recipe,
    reset_recipes_db,
    list_recipes,
    list_meal_plans,
    create_meal_plan,
)

# Single source of truth for seeded recipe data.
# Keys match the kwargs expected by crud.create_recipe.
RECIPES_TO_SEED = [
    {
        "name": "Classic Pancakes",
        "description": "Fluffy, classic pancakes from scratch.",
        "instructions": (
            "1. Mix dry ingredients. 2. Mix wet ingredients. "
            "3. Combine and cook on a griddle."
        ),
        "ingredients_data": [
            {"name": "Flour", "quantity": 1.5, "unit": "cups"},
            {"name": "Sugar", "quantity": 1, "unit": "tbsp"},
            {"name": "Baking Powder", "quantity": 2, "unit": "tsp"},
            {"name": "Salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "Milk", "quantity": 1.25, "unit": "cups"},
            {"name": "Egg", "quantity": 1, "unit": ""},
            {"name": "Butter", "quantity": 2, "unit": "tbsp"},
        ],
    },
    {
        "name": "Simple Omelette",
        "description": "A quick and easy two-egg omelette.",
        "instructions": (
            "1. Whisk eggs, water, salt, and pepper. "
            "2. Pour into a heated, oiled pan. 3. Cook until set, then fold."
        ),
        "ingredients_data": [
            {"name": "Eggs", "quantity": 2, "unit": ""},
            {"name": "Water", "quantity": 2, "unit": "tbsp"},
            {"name": "Salt", "quantity": 1, "unit": "pinch"},
            {"name": "Pepper", "quantity": 1, "unit": "pinch"},
            {"name": "Cheese", "quantity": 0.25, "unit": "cup"},
        ],
    },
]


def seed_database():
    """
    Resets and seeds the database with initial recipe data from RECIPES_TO_SEED.
    Always resets to ensure a clean state for tests/E2E.
    """
    # Reset the database to ensure a clean state
    print("Resetting recipes database...")
    reset_recipes_db()

    print(f"Seeding database with {len(RECIPES_TO_SEED)} recipes...")
    for recipe_data in RECIPES_TO_SEED:
        create_recipe(**recipe_data)

    print("Database seeding complete!")

    # Always attempt to seed the Weekly Meal Plan (idempotent inside)
    # even if recipes were already present (fixes early-return skip).
    seed_meal_plans()


def seed_meal_plans():
    """Seeds a sample meal plan using existing recipes (idempotent check)."""
    existing_plans = list_meal_plans()
    if any(
        "Weekly Meal Plan" in (getattr(mp, "name", "") or "") for mp in existing_plans
    ):
        print("Weekly Meal Plan already exists. Skipping meal plan seed.")
        return

    # Fetch current recipes (use local crud, not API)
    recipes = list_recipes() or []
    if not recipes:
        print("No recipes found to build meal plan seed.")
        return

    recipe_ids = [r.recipe_id for r in recipes[:2]]  # use up to the seeded ones
    plan = create_meal_plan(
        name="Weekly Meal Plan",
        description="E2E test plan containing seeded recipes.",
        recipe_ids=recipe_ids,
    )
    print(f"Seeded meal plan: {plan.name} (id={plan.meal_plan_id})")


if __name__ == "__main__":
    seed_database()
