"""
Database seeding script for the Meal Planner App using SQLAlchemy.
"""
from . import create_app
from .crud import create_recipe, reset_database

def seed_database():
    """
    Initializes and seeds the database with sample data.
    This function should be called within a Flask application context.
    """
    reset_database()

    # --- Create Sample Recipes ---
    create_recipe(
        name="Spaghetti Bolognese",
        description="A classic Italian meat-based sauce served with spaghetti.",
        instructions=(
            "1. Heat olive oil and cook onions and garlic.\n"
            "2. Add beef and cook until browned.\n"
            "3. Stir in tomatoes and simmer.\n"
            "4. Cook spaghetti and serve with sauce."
        ),
        ingredients_data=[
            {"name": "Spaghetti", "quantity": "200", "unit": "g"},
            {"name": "Minced Beef", "quantity": "500", "unit": "g"},
            {"name": "Chopped Tomatoes", "quantity": "400", "unit": "g"},
        ],
        source_url="https://example.com/spaghetti",
    )
    create_recipe(
        name="Classic Chicken Salad",
        description="A simple and delicious chicken salad.",
        instructions=(
            "1. Dice cooked chicken.\n"
            "2. Mix with mayonnaise, celery, and onion.\n"
            "3. Season and serve."
        ),
        ingredients_data=[
            {"name": "Cooked Chicken Breast", "quantity": "2", "unit": "cups"},
            {"name": "Mayonnaise", "quantity": "0.5", "unit": "cup"},
        ],
    )
    print("Database has been seeded with sample recipes.")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("Seeding database...")
        seed_database()
        print("Seeding complete.")
