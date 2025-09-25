"""
A script to seed the in-memory database with some initial data.
This is useful for development and for running end-to-end tests.
"""

from meal_planner_app.crud import create_recipe, reset_recipes_db


def seed_database():
    """
    Resets and seeds the database with initial recipe data.
    """
    # Reset the database to ensure a clean state
    print("Resetting recipes database...")
    reset_recipes_db()

    # Define the recipes to be added
    recipes_to_add = [
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

    print(f"Seeding database with {len(recipes_to_add)} recipes...")
    for recipe_data in recipes_to_add:
        create_recipe(**recipe_data)

    print("Database seeding complete!")


if __name__ == "__main__":
    seed_database()
