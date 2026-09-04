"""DAO tests: SQLite adapter behind MealPlannerDao protocols."""

import os
import tempfile
import unittest
import uuid

from meal_planner_app.dao.factory import create_dao
from meal_planner_app.models.ingredient import Ingredient, MasterIngredient
from meal_planner_app.models.meal_plan import MealPlan
from meal_planner_app.models.recipe import Recipe
from meal_planner_app.models.shopping_list import ShoppingList, ShoppingListItem


class TestIngredientDao(unittest.TestCase):
    """Master ingredient catalog persistence."""

    def setUp(self):
        self.dao = create_dao(":memory:")

    def tearDown(self):
        self.dao.close()

    def test_insert_and_find_by_id(self):
        saved = self.dao.ingredients.insert(
            MasterIngredient(name="Flour", default_unit="cups", location="Baking")
        )
        self.assertIsInstance(saved.ingredient_id, uuid.UUID)
        found = self.dao.ingredients.find_by_id(saved.ingredient_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Flour")
        self.assertEqual(found.default_unit, "cups")
        self.assertEqual(found.location, "Baking")

    def test_find_by_name(self):
        self.dao.ingredients.insert(MasterIngredient(name="Milk", default_unit="cups"))
        found = self.dao.ingredients.find_by_name("Milk")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Milk")
        self.assertIsNone(self.dao.ingredients.find_by_name("missing"))

    def test_find_all_sorted_by_name(self):
        self.dao.ingredients.insert(MasterIngredient(name="Salt"))
        self.dao.ingredients.insert(MasterIngredient(name="Eggs"))
        names = [i.name for i in self.dao.ingredients.find_all()]
        self.assertEqual(names, ["Eggs", "Salt"])

    def test_update_and_delete(self):
        saved = self.dao.ingredients.insert(MasterIngredient(name="Butter"))
        saved.default_unit = "tbsp"
        updated = self.dao.ingredients.update(saved)
        self.assertEqual(updated.default_unit, "tbsp")
        self.assertTrue(self.dao.ingredients.delete(saved.ingredient_id))
        self.assertIsNone(self.dao.ingredients.find_by_id(saved.ingredient_id))
        self.assertFalse(self.dao.ingredients.delete(saved.ingredient_id))

    def test_file_persists_across_connections(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            dao = create_dao(path)
            dao.ingredients.insert(MasterIngredient(name="Cheese"))
            dao.close()
            dao2 = create_dao(path)
            found = dao2.ingredients.find_by_name("Cheese")
            self.assertIsNotNone(found)
            dao2.close()
        finally:
            os.remove(path)


class TestRecipeDao(unittest.TestCase):
    """Recipes persist as rows linked to master ingredients."""

    def setUp(self):
        self.dao = create_dao(":memory:")
        self.flour = self.dao.ingredients.insert(
            MasterIngredient(name="Flour", default_unit="cups", location="Baking")
        )

    def tearDown(self):
        self.dao.close()

    def test_insert_recipe_with_ingredient_line(self):
        recipe = Recipe(
            name="Pancakes",
            instructions="Mix",
            ingredients=[
                Ingredient(
                    name="Flour",
                    quantity=1.5,
                    unit="cups",
                    location="Baking",
                    ingredient_id=self.flour.ingredient_id,
                )
            ],
        )
        saved = self.dao.recipes.insert(recipe)
        found = self.dao.recipes.find_by_id(saved.recipe_id)
        self.assertEqual(found.name, "Pancakes")
        self.assertEqual(len(found.ingredients), 1)
        self.assertEqual(found.ingredients[0].name, "Flour")
        self.assertEqual(found.ingredients[0].quantity, 1.5)
        self.assertEqual(found.ingredients[0].ingredient_id, self.flour.ingredient_id)

    def test_empty_line_unit_uses_default_unit(self):
        recipe = Recipe(
            name="Pancakes",
            instructions="Mix",
            ingredients=[
                Ingredient(
                    name="Flour",
                    quantity=1,
                    unit="",
                    ingredient_id=self.flour.ingredient_id,
                )
            ],
        )
        saved = self.dao.recipes.insert(recipe)
        found = self.dao.recipes.find_by_id(saved.recipe_id)
        self.assertEqual(found.ingredients[0].unit, "cups")

    def test_delete_ingredient_restricted_when_used(self):
        recipe = Recipe(
            name="Pancakes",
            instructions="Mix",
            ingredients=[
                Ingredient(
                    name="Flour",
                    quantity=1,
                    unit="cups",
                    ingredient_id=self.flour.ingredient_id,
                )
            ],
        )
        self.dao.recipes.insert(recipe)
        self.assertFalse(self.dao.ingredients.delete(self.flour.ingredient_id))
        self.assertIsNotNone(self.dao.ingredients.find_by_id(self.flour.ingredient_id))

    def test_delete_recipe_then_ingredient(self):
        recipe = Recipe(
            name="Pancakes",
            instructions="Mix",
            ingredients=[
                Ingredient(
                    name="Flour",
                    quantity=1,
                    unit="cups",
                    ingredient_id=self.flour.ingredient_id,
                )
            ],
        )
        saved = self.dao.recipes.insert(recipe)
        self.assertTrue(self.dao.recipes.delete(saved.recipe_id))
        self.assertTrue(self.dao.ingredients.delete(self.flour.ingredient_id))


class TestMealPlanAndShoppingListDao(unittest.TestCase):
    """Meal plans reference recipes; shopping lists snapshot items."""

    def setUp(self):
        self.dao = create_dao(":memory:")
        flour = self.dao.ingredients.insert(MasterIngredient(name="Flour"))
        self.recipe = self.dao.recipes.insert(
            Recipe(
                name="Pancakes",
                instructions="Mix",
                ingredients=[
                    Ingredient(
                        name="Flour",
                        quantity=1,
                        unit="cups",
                        ingredient_id=flour.ingredient_id,
                    )
                ],
            )
        )

    def tearDown(self):
        self.dao.close()

    def test_meal_plan_with_count(self):
        plan = MealPlan(
            name="Week",
            recipes=[{"recipe_id": self.recipe.recipe_id, "count": 2.0}],
        )
        saved = self.dao.meal_plans.insert(plan)
        found = self.dao.meal_plans.find_by_id(saved.meal_plan_id)
        self.assertEqual(found.name, "Week")
        self.assertEqual(len(found.recipes), 1)
        self.assertEqual(found.recipes[0]["recipe_id"], self.recipe.recipe_id)
        self.assertEqual(found.recipes[0]["count"], 2.0)

    def test_meal_plan_recipes_preserve_insertion_order(self):
        """Reload must keep insert order, not PRIMARY KEY (recipe_id) order."""
        other = self.dao.recipes.insert(
            Recipe(name="Waffles", instructions="Cook", ingredients=[])
        )
        rid_a, rid_b = self.recipe.recipe_id, other.recipe_id
        if str(rid_a) < str(rid_b):
            first, second = rid_b, rid_a
        else:
            first, second = rid_a, rid_b
        plan = MealPlan(
            name="Order",
            recipes=[
                {"recipe_id": first, "count": 1.5},
                {"recipe_id": second, "count": 0.25},
            ],
        )
        saved = self.dao.meal_plans.insert(plan)
        found = self.dao.meal_plans.find_by_id(saved.meal_plan_id)
        self.assertEqual([e["count"] for e in found.recipes], [1.5, 0.25])
        self.assertEqual(found.recipes[0]["recipe_id"], first)
        self.assertEqual(found.recipes[1]["recipe_id"], second)

    def test_shopping_list_snapshot_and_quantity_list(self):
        sl = ShoppingList(
            name="Groceries",
            meal_plan_id=None,
            items=[
                ShoppingListItem(name="Flour", quantity=1.5, unit="cups"),
                ShoppingListItem(name="Salt", quantity=["1", "pinch"], unit=""),
            ],
        )
        saved = self.dao.shopping_lists.insert(sl)
        found = self.dao.shopping_lists.find_by_id(saved.id)
        self.assertEqual(found.name, "Groceries")
        self.assertEqual(len(found.items), 2)
        self.assertEqual(found.items[0].quantity, 1.5)
        self.assertEqual(found.items[1].quantity, ["1", "pinch"])

    def test_delete_meal_plan_nulls_shopping_list_fk(self):
        plan = self.dao.meal_plans.insert(
            MealPlan(
                name="Week",
                recipes=[{"recipe_id": self.recipe.recipe_id, "count": 1.0}],
            )
        )
        sl = self.dao.shopping_lists.insert(
            ShoppingList(name="From plan", meal_plan_id=plan.meal_plan_id, items=[])
        )
        self.assertTrue(self.dao.meal_plans.delete(plan.meal_plan_id))
        found = self.dao.shopping_lists.find_by_id(sl.id)
        self.assertIsNotNone(found)
        self.assertIsNone(found.meal_plan_id)
