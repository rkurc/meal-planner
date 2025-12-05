import json
import logging
import urllib.request
import urllib.error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:5000/api"


def get_recipes():
    """Fetches existing recipes from the API."""
    try:
        with urllib.request.urlopen(f"{API_BASE_URL}/recipes") as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return data
    except urllib.error.URLError as e:
        logger.error(f"Failed to connect to API: {e}")
        return None
    return []


def create_recipe(recipe_data):
    """Creates a recipe via the API."""
    url = f"{API_BASE_URL}/recipes"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(recipe_data).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 201:
                logger.info(f"Created recipe: {recipe_data['name']}")
                return True
    except urllib.error.HTTPError as e:
        logger.error(
            f"Failed to create recipe {recipe_data['name']}: {e.code} {e.reason}"
        )
        logger.error(e.read().decode())
    except urllib.error.URLError as e:
        logger.error(f"Failed to connect to API: {e}")
    return False


def seed_database():
    """Seeds the database with initial recipes via API."""
    existing_recipes = get_recipes()

    if existing_recipes is None:
        logger.error("Could not verify existing recipes. Is the server running?")
        return

    if existing_recipes:
        logger.info(
            f"Database already contains {len(existing_recipes)} recipes. Skipping seed."
        )
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
            "instructions": "1. Butter bread. 2. Place cheese between slices. 3. Grill until golden.",
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

    logger.info("Database seeding completed.")


if __name__ == "__main__":
    seed_database()
