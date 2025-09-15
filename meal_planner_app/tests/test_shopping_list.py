"""
Tests for the shopping list generation functionality, now using a test database.
"""

from .base import BaseTestCase
from meal_planner_app import crud, db


class TestShoppingList(BaseTestCase):
    """Tests for the generate_shopping_list function."""

    def setUp(self):
        """Set up a variety of recipes and meal plans for testing."""
        super().setUp()
        self.recipe1 = crud.create_recipe(
            name="Pancakes",
            instructions="Mix and cook.",
            ingredients_data=[
                {"name": "Flour", "quantity": 2, "unit": "cup"},
                {"name": "Sugar", "quantity": 0.5, "unit": "cup"},
            ],
        )
        self.meal_plan1 = crud.create_meal_plan(
            name="Breakfast Week", recipe_ids=[self.recipe1.id]
        )
        db.session.commit()

    def find_ingredient(self, shopping_list, name, unit):
        """Helper function to find an ingredient in a shopping list."""
        for item in shopping_list:
            if item["name"] == name and item["unit"] == unit:
                return item
        return None

    def test_generate_shopping_list_basic_aggregation(self):
        """Test basic aggregation of numeric quantities for the same ingredient."""
        shopping_list = crud.generate_shopping_list(self.meal_plan1.id)
        self.assertIsNotNone(shopping_list)

        flour = self.find_ingredient(shopping_list, "Flour", "cup")
        self.assertIsNotNone(flour)
        self.assertEqual(flour["quantity"], "2.0")

        sugar = self.find_ingredient(shopping_list, "Sugar", "cup")
        self.assertIsNotNone(sugar)
        self.assertEqual(sugar["quantity"], "0.5")
