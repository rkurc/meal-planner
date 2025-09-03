"""
Tests for the shopping list generation functionality in crud.py.
"""

import unittest
import uuid

from meal_planner_app import crud


class TestShoppingList(
    unittest.TestCase
):  # pylint: disable=too-many-instance-attributes
    """Tests for the generate_shopping_list function."""

    def setUp(self):
        """Set up a variety of recipes and meal plans for testing."""
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()

        # Recipe 1: Basic ingredients
        self.recipe1 = crud.create_recipe(
            name="Pancakes",
            instructions="Mix and cook.",
            ingredients_data=[
                {"name": "Flour", "quantity": 2, "unit": "cup"},
                {"name": "Sugar", "quantity": 0.5, "unit": "cup"},
                {"name": "Egg", "quantity": 1, "unit": "pc"},
            ],
        )

        # Recipe 2: More ingredients, some overlapping with Recipe 1, some non-numeric
        self.recipe2 = crud.create_recipe(
            name="Deluxe Omelette",
            instructions="Whisk eggs, add fillings, cook.",
            ingredients_data=[
                {"name": "Egg", "quantity": 3, "unit": "pc"},
                {"name": "Cheese", "quantity": 50, "unit": "g"},
                {"name": "Salt", "quantity": "to taste", "unit": ""},
                {"name": "Pepper", "quantity": "a pinch", "unit": "sprinkle"},
            ],
        )

        # Recipe 3: Different units for same ingredient name, another non-numeric
        self.recipe3 = crud.create_recipe(
            name="Milkshake",
            instructions="Blend.",
            ingredients_data=[
                {"name": "Milk", "quantity": 200, "unit": "ml"},
                {"name": "Sugar", "quantity": 2, "unit": "tbsp"},
                {"name": "Ice Cream", "quantity": "2 scoops", "unit": ""},
            ],
        )

        # Recipe 4: No ingredients
        self.recipe4_no_ing = crud.create_recipe(
            name="Water", instructions="Pour water."
        )

        self.meal_plan1 = crud.create_meal_plan(name="Breakfast Week")
        crud.add_recipe_to_meal_plan(
            self.meal_plan1.meal_plan_id, self.recipe1.recipe_id
        )
        crud.add_recipe_to_meal_plan(
            self.meal_plan1.meal_plan_id, self.recipe2.recipe_id
        )

        self.meal_plan2_complex = crud.create_meal_plan(name="Full Menu")
        crud.add_recipe_to_meal_plan(
            self.meal_plan2_complex.meal_plan_id, self.recipe1.recipe_id
        )  # Pancakes
        crud.add_recipe_to_meal_plan(
            self.meal_plan2_complex.meal_plan_id, self.recipe2.recipe_id
        )  # Omelette
        crud.add_recipe_to_meal_plan(
            self.meal_plan2_complex.meal_plan_id, self.recipe3.recipe_id
        )  # Milkshake

        self.meal_plan_empty_recipes = crud.create_meal_plan(name="Empty Recipes Plan")
        crud.add_recipe_to_meal_plan(
            self.meal_plan_empty_recipes.meal_plan_id, self.recipe4_no_ing.recipe_id
        )

        self.meal_plan_no_recipes = crud.create_meal_plan(name="No Recipes Plan")

    def find_ingredient(self, shopping_list, name, unit):
        """Helper function to find an ingredient in a shopping list."""
        for item in shopping_list:
            if item["name"] == name and item["unit"] == unit:
                return item
        return None

    def test_generate_shopping_list_basic_aggregation(self):
        """Test basic aggregation of numeric quantities for the same ingredient."""
        shopping_list = crud.generate_shopping_list(self.meal_plan1.meal_plan_id)
        self.assertIsNotNone(shopping_list)

        # Flour: 2 cup (from R1)
        flour = self.find_ingredient(shopping_list, "Flour", "cup")
        self.assertIsNotNone(flour)
        self.assertEqual(flour["quantity"], 2)

        # Sugar: 0.5 cup (from R1)
        sugar = self.find_ingredient(shopping_list, "Sugar", "cup")
        self.assertIsNotNone(sugar)
        self.assertEqual(sugar["quantity"], 0.5)

        # Egg: 1 pc (R1) + 3 pc (R2) = 4 pc
        egg = self.find_ingredient(shopping_list, "Egg", "pc")
        self.assertIsNotNone(egg)
        self.assertEqual(egg["quantity"], 4)

        # Cheese: 50 g (from R2)
        cheese = self.find_ingredient(shopping_list, "Cheese", "g")
        self.assertIsNotNone(cheese)
        self.assertEqual(cheese["quantity"], 50)

        # Salt: 'to taste' (from R2)
        salt = self.find_ingredient(shopping_list, "Salt", "")
        self.assertIsNotNone(salt)
        self.assertEqual(salt["quantity"], "to taste")

        # Pepper: 'a pinch' (from R2)
        pepper = self.find_ingredient(shopping_list, "Pepper", "sprinkle")
        self.assertIsNotNone(pepper)
        self.assertEqual(pepper["quantity"], "a pinch")

        self.assertEqual(
            len(shopping_list), 6
        )  # Flour, Sugar (cup), Egg, Cheese, Salt, Pepper

    def test_generate_shopping_list_complex_aggregation(self):
        """Test aggregation with different units and non-numeric quantities."""
        shopping_list = crud.generate_shopping_list(
            self.meal_plan2_complex.meal_plan_id
        )
        self.assertIsNotNone(shopping_list)

        # Check some key aggregations
        # Egg: 1 pc (R1) + 3 pc (R2) = 4 pc
        egg = self.find_ingredient(shopping_list, "Egg", "pc")
        self.assertIsNotNone(egg)
        self.assertEqual(egg["quantity"], 4)

        # Sugar (cup): 0.5 cup (R1)
        sugar_cup = self.find_ingredient(shopping_list, "Sugar", "cup")
        self.assertIsNotNone(sugar_cup)
        self.assertEqual(sugar_cup["quantity"], 0.5)

        # Sugar (tbsp): 2 tbsp (R3)
        sugar_tbsp = self.find_ingredient(shopping_list, "Sugar", "tbsp")
        self.assertIsNotNone(sugar_tbsp)
        self.assertEqual(sugar_tbsp["quantity"], 2)

        # Milk (ml): 200 ml (R3)
        milk = self.find_ingredient(shopping_list, "Milk", "ml")
        self.assertIsNotNone(milk)
        self.assertEqual(milk["quantity"], 200)

        # Ice Cream: '2 scoops' (R3)
        ice_cream = self.find_ingredient(shopping_list, "Ice Cream", "")
        self.assertIsNotNone(ice_cream)
        self.assertEqual(ice_cream["quantity"], "2 scoops")

        # Expected number of unique ingredient_key items
        # R1: Flour_cup, Sugar_cup, Egg_pc (3)
        # R2: Egg_pc (exists), Cheese_g, Salt_, Pepper_sprinkle (3 new)
        # R3: Milk_ml, Sugar_tbsp, Ice Cream_ (3 new)
        # Total = 3 + 3 + 3 = 9
        self.assertEqual(len(shopping_list), 9)

    def test_shopping_list_with_mixed_numeric_non_numeric(self):
        """Test aggregation when an ingredient has both numeric and non-numeric quantities."""
        # Create a recipe that will cause mixed types for 'Flour_cup'
        recipe_extra = crud.create_recipe(
            name="Extra Flour",
            instructions="Add more flour.",
            ingredients_data=[
                {"name": "Flour", "quantity": "a bit more", "unit": "cup"}
            ],
        )
        crud.add_recipe_to_meal_plan(
            self.meal_plan1.meal_plan_id, recipe_extra.recipe_id
        )
        # Now meal_plan1 has:
        # R1: Flour, 2 cup
        # R2: (no flour)
        # Extra: Flour, 'a bit more' cup

        shopping_list = crud.generate_shopping_list(self.meal_plan1.meal_plan_id)
        flour_cup = self.find_ingredient(shopping_list, "Flour", "cup")
        self.assertIsNotNone(flour_cup)
        self.assertIsInstance(flour_cup["quantity"], list)
        self.assertIn(
            "2.0", flour_cup["quantity"]
        )  # Original numeric becomes string in list
        self.assertIn("a bit more", flour_cup["quantity"])

    def test_shopping_list_empty_meal_plan(self):
        """Test generating a shopping list for a meal plan with no recipes."""
        shopping_list = crud.generate_shopping_list(
            self.meal_plan_no_recipes.meal_plan_id
        )
        self.assertIsNotNone(shopping_list)
        self.assertEqual(len(shopping_list), 0)

    def test_shopping_list_meal_plan_with_empty_recipes(self):
        """Test generating a shopping list for a meal plan with recipes that have no ingredients."""
        shopping_list = crud.generate_shopping_list(
            self.meal_plan_empty_recipes.meal_plan_id
        )
        self.assertIsNotNone(shopping_list)
        self.assertEqual(len(shopping_list), 0)

    def test_shopping_list_non_existent_meal_plan(self):
        """Test generating a shopping list for a non-existent meal plan ID."""
        non_existent_id = uuid.uuid4()
        shopping_list = crud.generate_shopping_list(non_existent_id)
        self.assertIsNone(shopping_list)


if __name__ == "__main__":
    unittest.main()
