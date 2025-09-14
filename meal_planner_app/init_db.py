"""
Initializes the database by creating all the tables.
"""
from . import create_app, db
from .models import recipe, ingredient, meal_plan, shopping_list

app = create_app()
with app.app_context():
    db.create_all()

print("Database tables created.")
