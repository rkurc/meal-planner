"""
Tests for the CRUD operations in crud.py, now using a test database.
"""

from .base import BaseTestCase
from meal_planner_app import crud, db


class TestRecipeCRUD(BaseTestCase):
    """Tests for Recipe CRUD operations with a database."""

    def test_create_and_get_recipe(self):
        """Test creating a recipe and then retrieving it."""
        recipe1 = crud.create_recipe(
            name="Pancakes",
            instructions="Mix and cook.",
            description="Fluffy pancakes.",
        )
        self.assertIsNotNone(recipe1.id)
        self.assertEqual(recipe1.name, "Pancakes")

        retrieved_recipe = crud.get_recipe(recipe1.id)
        self.assertIsNotNone(retrieved_recipe)
        self.assertEqual(retrieved_recipe.id, recipe1.id)
        self.assertEqual(retrieved_recipe.name, "Pancakes")


class TestMealPlanCRUD(BaseTestCase):
    """Tests for MealPlan CRUD operations with a database."""

    def setUp(self):
        """Override setUp to create some recipes."""
        super().setUp()
        self.recipe1 = crud.create_recipe(name="R1", instructions="I1")
        self.recipe2 = crud.create_recipe(name="R2", instructions="I2")
        db.session.commit()

    def test_create_and_get_meal_plan(self):
        """Test creating a meal plan and then retrieving it."""
        mp = crud.create_meal_plan(name="Weekly Plan 1")
        self.assertIsNotNone(mp.id)
        self.assertEqual(mp.name, "Weekly Plan 1")
        self.assertEqual(len(mp.recipes), 0)

        retrieved_mp = crud.get_meal_plan(mp.id)
        self.assertIsNotNone(retrieved_mp)
        self.assertEqual(retrieved_mp.id, mp.id)
        self.assertEqual(retrieved_mp.name, "Weekly Plan 1")
