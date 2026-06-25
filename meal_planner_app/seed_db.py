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


def create_meal_plan(plan_data):
    """Creates a meal plan via the API (for E2E seeding)."""
    url = f"{API_BASE_URL}/meal-plans"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(plan_data).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 201:
                logger.info("Created meal plan: %s", plan_data.get("name"))
                return True
    except urllib.error.HTTPError as e:
        logger.error(
            "Failed to create meal plan %s: %s %s",
            plan_data.get("name"),
            e.code,
            e.reason,
        )
        logger.error(e.read().decode())
    except urllib.error.URLError as e:
        logger.error("Failed to connect to API: %s", e)
    return False


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

    logger.info("Seeding database with initial recipes via API...")

    recipes_to_create = [
        {
            "name": "Tomato Pasta",
            "description": "A simple and delicious pasta dish with fresh tomatoes.",
            "instructions": "1. Boil pasta. 2. Cook tomatoes. 3. Mix together.",
            "ingredients": [
                {"name": "Pasta", "quantity": 500, "unit": "g"},
                {"name": "Tomatoes", "quantity": 4, "unit": "whole"},
                {"name": "Olive Oil", "quantity": 2, "unit": "tbsp"},
                {"name": "Garlic", "quantity": 2, "unit": "cloves"},
            ],
            "source_url": "http://example.com/tomato-pasta",
        },
        {
            "name": "Grilled Cheese Sandwich",
            "description": "Classic comfort food.",
            "instructions": (
                "1. Butter bread. 2. Place cheese between slices. 3. Grill until golden."
            ),
            "ingredients": [
                {"name": "Bread", "quantity": 2, "unit": "slices"},
                {"name": "Cheddar Cheese", "quantity": 2, "unit": "slices"},
                {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            ],
            "source_url": "http://example.com/grilled-cheese",
        },
        {
            "name": "Fruit Salad",
            "description": "Fresh and healthy dessert.",
            "instructions": "1. Chop all fruits. 2. Mix in a bowl. 3. Serve chilled.",
            "ingredients": [
                {"name": "Apple", "quantity": 1, "unit": "whole"},
                {"name": "Banana", "quantity": 1, "unit": "whole"},
                {"name": "Orange", "quantity": 1, "unit": "whole"},
                {"name": "Grapes", "quantity": 100, "unit": "g"},
            ],
            "source_url": "http://example.com/fruit-salad",
        },
    ]

    for recipe in recipes_to_create:
        create_recipe(recipe)

    # Seed a "Weekly Meal Plan" for E2E tests (Critical from prior review)
    logger.info("Creating Weekly Meal Plan for E2E tests...")
    existing_recipes = get_recipes() or []
    recipe_ids = [r.get("id") for r in existing_recipes if r.get("id")]
    if recipe_ids:
        create_meal_plan(
            {
                "name": "Weekly Meal Plan",
                "description": "Seeded weekly plan for E2E tests",
                "recipe_ids": recipe_ids,
            }
        )
    else:
        logger.warning("No recipe IDs available; skipping meal plan seed.")

    logger.info("Database seeding completed.")


if __name__ == "__main__":
    seed_database()
