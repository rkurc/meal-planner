import unittest
import uuid

from meal_planner_app.models.recipe import Recipe
from meal_planner_app.models.ingredient import Ingredient
from meal_planner_app import crud

class TestRecipeCRUD(unittest.TestCase):

    def setUp(self):
        """Clear the in-memory database before each test."""
        crud.reset_recipes_db()

    def test_create_and_get_recipe(self):
        """Test creating a recipe and then retrieving it."""
        recipe1 = crud.create_recipe(name="Pancakes",
                                     instructions="Mix and cook.",
                                     description="Fluffy pancakes.")
        self.assertIsNotNone(recipe1.id)
        self.assertEqual(recipe1.name, "Pancakes")

        retrieved_recipe = crud.get_recipe(recipe1.id)
        self.assertIsNotNone(retrieved_recipe)
        self.assertEqual(retrieved_recipe.id, recipe1.id)
        self.assertEqual(retrieved_recipe.name, "Pancakes")

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients."""
        ingredients_data = [
            {'name': 'Flour', 'quantity': 2, 'unit': 'cups'},
            {'name': 'Sugar', 'quantity': '0.25', 'unit': 'cup'}
        ]
        recipe = crud.create_recipe(name="Cookies",
                                    instructions="Mix and bake.",
                                    ingredients_data=ingredients_data)
        self.assertIsNotNone(recipe)
        self.assertEqual(len(recipe.ingredients), 2)
        self.assertIsInstance(recipe.ingredients[0], Ingredient)
        self.assertEqual(recipe.ingredients[0].name, "Flour")
        self.assertEqual(recipe.ingredients[0].quantity, 2)
        self.assertEqual(recipe.ingredients[1].name, "Sugar")
        self.assertEqual(recipe.ingredients[1].quantity, '0.25')


    def test_update_recipe(self):
        """Test updating various fields of a recipe."""
        recipe = crud.create_recipe(name="Old Soup", instructions="Old instructions.")

        updated_name = "New Soup"
        updated_instructions = "New instructions."
        updated_description = "A tasty new soup."
        new_ingredients_data = [{'name': 'Carrot', 'quantity': 1, 'unit': 'pc'}]

        updated_recipe = crud.update_recipe(recipe.id,
                                            name=updated_name,
                                            instructions=updated_instructions,
                                            description=updated_description,
                                            ingredients_data=new_ingredients_data)
        self.assertIsNotNone(updated_recipe)
        self.assertEqual(updated_recipe.name, updated_name)
        self.assertEqual(updated_recipe.instructions, updated_instructions)
        self.assertEqual(updated_recipe.description, updated_description)
        self.assertEqual(len(updated_recipe.ingredients), 1)
        self.assertEqual(updated_recipe.ingredients[0].name, "Carrot")

        # Test updating only one field
        further_updated_recipe = crud.update_recipe(recipe.id, source_url="http://example.com/soup")
        self.assertIsNotNone(further_updated_recipe)
        self.assertEqual(further_updated_recipe.source_url, "http://example.com/soup")
        self.assertEqual(further_updated_recipe.name, updated_name) # Check other fields remain

    def test_delete_recipe(self):
        """Test deleting a recipe."""
        recipe1 = crud.create_recipe(name="To Be Deleted", instructions="...")
        recipe2 = crud.create_recipe(name="To Keep", instructions="...")

        self.assertTrue(crud.delete_recipe(recipe1.id))
        self.assertIsNone(crud.get_recipe(recipe1.id))
        self.assertIsNotNone(crud.get_recipe(recipe2.id)) # Ensure other recipe is not deleted
        self.assertEqual(len(crud.list_recipes()), 1)

    def test_list_recipes(self):
        """Test listing all recipes."""
        self.assertEqual(len(crud.list_recipes()), 0) # Initially empty
        crud.create_recipe(name="Pasta", instructions="Boil and serve.")
        crud.create_recipe(name="Salad", instructions="Chop and mix.")

        recipes = crud.list_recipes()
        self.assertEqual(len(recipes), 2)
        self.assertTrue(any(r.name == "Pasta" for r in recipes))
        self.assertTrue(any(r.name == "Salad" for r in recipes))

    def test_get_nonexistent_recipe(self):
        """Test that get_recipe returns None for an invalid ID."""
        non_existent_id = uuid.uuid4()
        self.assertIsNone(crud.get_recipe(non_existent_id))

    def test_update_nonexistent_recipe(self):
        """Test that update_recipe returns None for an invalid ID."""
        non_existent_id = uuid.uuid4()
        updated_recipe = crud.update_recipe(non_existent_id, name="Should Not Work")
        self.assertIsNone(updated_recipe)

    def test_delete_nonexistent_recipe(self):
        """Test that delete_recipe returns False for an invalid ID."""
        non_existent_id = uuid.uuid4()
        self.assertFalse(crud.delete_recipe(non_existent_id))

if __name__ == '__main__':
    unittest.main()


class TestMealPlanCRUD(unittest.TestCase):

    def setUp(self):
        """Clear the in-memory databases before each test."""
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()
        # Create some sample recipes for testing meal plan functions
        self.recipe1 = crud.create_recipe(name="R1", instructions="I1")
        self.recipe2 = crud.create_recipe(name="R2", instructions="I2")

    def test_create_and_get_meal_plan(self):
        mp = crud.create_meal_plan(name="Weekly Plan 1")
        self.assertIsNotNone(mp.id)
        self.assertEqual(mp.name, "Weekly Plan 1")
        self.assertEqual(len(mp.recipe_ids), 0)

        retrieved_mp = crud.get_meal_plan(mp.id)
        self.assertIsNotNone(retrieved_mp)
        self.assertEqual(retrieved_mp.id, mp.id)
        self.assertEqual(retrieved_mp.name, "Weekly Plan 1")

    def test_list_meal_plans(self):
        self.assertEqual(len(crud.list_meal_plans()), 0)
        crud.create_meal_plan(name="MP1")
        crud.create_meal_plan(name="MP2")
        self.assertEqual(len(crud.list_meal_plans()), 2)

    def test_add_recipe_to_meal_plan(self):
        mp = crud.create_meal_plan(name="My Plan")

        # Add valid recipe
        updated_mp = crud.add_recipe_to_meal_plan(mp.id, self.recipe1.id)
        self.assertIsNotNone(updated_mp)
        self.assertIn(self.recipe1.id, updated_mp.recipe_ids)

        # Add another valid recipe
        updated_mp = crud.add_recipe_to_meal_plan(mp.id, self.recipe2.id)
        self.assertIn(self.recipe2.id, updated_mp.recipe_ids)
        self.assertEqual(len(updated_mp.recipe_ids), 2)

        # Add existing recipe again (should not duplicate)
        updated_mp = crud.add_recipe_to_meal_plan(mp.id, self.recipe1.id)
        self.assertEqual(len(updated_mp.recipe_ids), 2)

        # Add to non-existent meal plan
        non_existent_mp_id = uuid.uuid4()
        self.assertIsNone(crud.add_recipe_to_meal_plan(non_existent_mp_id, self.recipe1.id))

        # Add non-existent recipe to existing meal plan
        non_existent_recipe_id = uuid.uuid4()
        # Current crud.add_recipe_to_meal_plan returns the meal_plan even if recipe not found.
        # This behavior might be acceptable, or could be changed to return None or raise error.
        # For now, test current behavior:
        updated_mp_with_non_recipe = crud.add_recipe_to_meal_plan(mp.id, non_existent_recipe_id)
        self.assertIsNotNone(updated_mp_with_non_recipe) # Meal plan itself is found
        self.assertNotIn(non_existent_recipe_id, updated_mp_with_non_recipe.recipe_ids) # Non-existent recipe should not be added


    def test_remove_recipe_from_meal_plan(self):
        mp = crud.create_meal_plan(name="Plan With Recipes")
        crud.add_recipe_to_meal_plan(mp.id, self.recipe1.id)
        crud.add_recipe_to_meal_plan(mp.id, self.recipe2.id)
        self.assertEqual(len(mp.recipe_ids), 2)

        # Remove existing recipe
        updated_mp = crud.remove_recipe_from_meal_plan(mp.id, self.recipe1.id)
        self.assertIsNotNone(updated_mp)
        self.assertNotIn(self.recipe1.id, updated_mp.recipe_ids)
        self.assertEqual(len(updated_mp.recipe_ids), 1)

        # Remove non-existent recipe from plan
        non_existent_recipe_id = uuid.uuid4()
        updated_mp = crud.remove_recipe_from_meal_plan(mp.id, non_existent_recipe_id)
        self.assertEqual(len(updated_mp.recipe_ids), 1) # Count should remain the same

        # Remove from non-existent meal plan
        self.assertIsNone(crud.remove_recipe_from_meal_plan(uuid.uuid4(), self.recipe1.id))

    def test_delete_meal_plan(self):
        mp1 = crud.create_meal_plan(name="To Delete")
        mp2 = crud.create_meal_plan(name="To Keep")
        self.assertTrue(crud.delete_meal_plan(mp1.id))
        self.assertIsNone(crud.get_meal_plan(mp1.id))
        self.assertIsNotNone(crud.get_meal_plan(mp2.id))
        self.assertEqual(len(crud.list_meal_plans()), 1)

        # Delete non-existent
        self.assertFalse(crud.delete_meal_plan(uuid.uuid4()))

    def test_update_meal_plan_name(self):
        mp = crud.create_meal_plan(name="Old Name")
        updated_mp = crud.update_meal_plan_name(mp.id, "New Name")
        self.assertIsNotNone(updated_mp)
        self.assertEqual(updated_mp.name, "New Name")
        self.assertEqual(crud.get_meal_plan(mp.id).name, "New Name")

        # Update non-existent
        self.assertIsNone(crud.update_meal_plan_name(uuid.uuid4(), "Doesn't Matter"))


class TestRecipeSearch(unittest.TestCase):

    def setUp(self):
        crud.reset_recipes_db()
        self.recipe1 = crud.create_recipe(
            name="Classic Pancakes",
            description="Fluffy and delicious breakfast pancakes.",
            ingredients_data=[
                {'name': 'Flour', 'quantity': 1, 'unit': 'cup'},
                {'name': 'Milk', 'quantity': 1, 'unit': 'cup'},
                {'name': 'Egg', 'quantity': 1, 'unit': 'pc'}
            ],
            instructions="Mix and cook."
        )
        self.recipe2 = crud.create_recipe(
            name="Spicy Chicken Soup",
            description="A hearty and spicy chicken soup with vegetables.",
            ingredients_data=[
                {'name': 'Chicken Breast', 'quantity': 200, 'unit': 'g'},
                {'name': 'Carrot', 'quantity': 1, 'unit': 'pc'},
                {'name': 'Celery', 'quantity': 1, 'unit': 'stalk'},
                {'name': 'Chili Flakes', 'quantity': 1, 'unit': 'tsp'}
            ],
            instructions="Boil chicken, add veggies and spice."
        )
        self.recipe3 = crud.create_recipe(
            name="Simple Salad",
            description="A quick and easy green salad.",
            ingredients_data=[
                {'name': 'Lettuce', 'quantity': 1, 'unit': 'head'},
                {'name': 'Tomato', 'quantity': 2, 'unit': 'pc'},
                {'name': 'Milk', 'quantity': 'for dressing', 'unit': 'optional'} # Different 'Milk'
            ],
            instructions="Toss ingredients."
        )
        self.recipe4_no_desc = crud.create_recipe(
            name="Boiled Egg",
            ingredients_data=[{'name': 'Egg', 'quantity': 1, 'unit': 'pc'}],
            instructions="Boil egg."
        )


    def test_search_by_full_name(self):
        results = crud.search_recipes("Classic Pancakes")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.recipe1.id)

    def test_search_by_partial_name(self):
        results = crud.search_recipes("pancake") # Case-insensitive
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.recipe1.id)

    def test_search_by_keyword_in_description(self):
        results = crud.search_recipes("delicious breakfast")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.recipe1.id)

        results_spicy = crud.search_recipes("SPICY")
        self.assertEqual(len(results_spicy), 1)
        self.assertEqual(results_spicy[0].id, self.recipe2.id)

    def test_search_by_ingredient_name(self):
        results = crud.search_recipes("Milk")
        self.assertEqual(len(results), 2) # Pancakes and Simple Salad
        self.assertIn(self.recipe1, results)
        self.assertIn(self.recipe3, results)

        results_flour = crud.search_recipes("flour")
        self.assertEqual(len(results_flour), 1)
        self.assertEqual(results_flour[0].id, self.recipe1.id)

    def test_search_multiple_results(self):
        results = crud.search_recipes("egg") # Pancakes, Spicy Chicken Soup (ingredient name not desc), Boiled Egg
        self.assertEqual(len(results), 2) # Recipe1, Recipe4_no_desc (Boiled Egg)
                                          # R2 Chicken Soup does not have 'egg' in name/desc, and 'Chicken Breast' is the ingredient.
                                          # Oh, I made a mistake in the test logic. My recipe1 and recipe4 have "Egg" as an ingredient.
                                          # Let's re-verify. Recipe1 (Pancakes) has "Egg". Recipe4 (Boiled Egg) has "Egg".
                                          # Recipe2 (Spicy Chicken Soup) does not have "Egg" as ingredient.
        # Correcting the assertion:
        self.assertIn(self.recipe1, results) # Pancakes has "Egg"
        self.assertIn(self.recipe4_no_desc, results) # Boiled Egg has "Egg"

    def test_search_single_result(self):
        results = crud.search_recipes("Chili Flakes")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.recipe2.id)

    def test_search_no_results(self):
        results = crud.search_recipes("NonExistentRecipeXYZ")
        self.assertEqual(len(results), 0)

    def test_search_empty_query(self):
        results_empty = crud.search_recipes("")
        self.assertEqual(len(results_empty), 0) # As per current implementation

        results_space = crud.search_recipes("   ")
        self.assertEqual(len(results_space), 0) # As per current implementation

    def test_search_query_matches_multiple_fields_in_same_recipe(self):
        # Recipe1: "Classic Pancakes", description "Fluffy and delicious breakfast pancakes.", ingredient "Flour"
        results = crud.search_recipes("pancakes") # Matches name and description
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.recipe1.id)

        # What if query matches name and an ingredient?
        # e.g. Recipe named "Apple Pie" with ingredient "Apple"
        # My current setup: recipe1 "Classic Pancakes" has "Flour".
        # If I search "Flour", it matches recipe1 by ingredient.
        # If I search "Pancakes", it matches recipe1 by name & desc.
        # The set `matching_recipes_ids` handles this.

    def test_search_recipe_with_no_description(self):
        results = crud.search_recipes("Boiled") # Matches name of recipe4_no_desc
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.recipe4_no_desc.id)

        # Search for something that would only be in description
        results_desc_only = crud.search_recipes("Fluffy")
        self.assertEqual(len(results_desc_only), 1)
        self.assertEqual(results_desc_only[0].id, self.recipe1.id)
        # Ensure recipe4 (no desc) is not found by a description-only term
        self.assertNotIn(self.recipe4_no_desc, results_desc_only)

    def test_ingredient_search_case_insensitivity(self):
        results = crud.search_recipes("chicken breast")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.recipe2.id)

    # --- Tests for Advanced Ingredient Filter ---

    def test_search_with_ingredient_filter(self):
        # Search "soup" (matches R2), filter by ingredient "carrot" (matches R2)
        results = crud.search_recipes(query="soup", filter_ingredient="carrot")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.recipe2.id)

    def test_search_with_ingredient_filter_no_match_in_query_results(self):
        # Search "soup" (matches R2), filter by "flour" (not in R2)
        results = crud.search_recipes(query="soup", filter_ingredient="flour")
        self.assertEqual(len(results), 0)

    def test_search_with_ingredient_filter_query_empty(self):
        # No query, filter by "Milk" (matches R1, R3)
        results = crud.search_recipes(query="", filter_ingredient="Milk")
        self.assertEqual(len(results), 2)
        self.assertIn(self.recipe1, results)
        self.assertIn(self.recipe3, results)

    def test_search_with_ingredient_filter_query_empty_no_results(self):
        # No query, filter by "NonExistentIngredient"
        results = crud.search_recipes(query="", filter_ingredient="NonExistentIngredient")
        self.assertEqual(len(results), 0)

    def test_search_with_ingredient_filter_both_present(self):
        # Search "Classic" (matches R1), filter by "Milk" (matches R1)
        results = crud.search_recipes(query="Classic", filter_ingredient="Milk")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.recipe1.id)

    def test_search_with_ingredient_filter_case_insensitivity(self):
        # Search "classic" (matches R1), filter by "milk" (matches R1)
        results = crud.search_recipes(query="classic", filter_ingredient="milk")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.recipe1.id)

    def test_search_with_ingredient_filter_empty_filter(self):
        # Search "soup", empty ingredient filter (should behave like no filter)
        results = crud.search_recipes(query="soup", filter_ingredient=" ")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.recipe2.id)

        results_none = crud.search_recipes(query="soup", filter_ingredient=None)
        self.assertEqual(len(results_none), 1)
        self.assertEqual(results_none[0].id, self.recipe2.id)

    def test_search_both_empty_query_and_filter(self):
        # Both query and filter are empty or whitespace
        results = crud.search_recipes(query="", filter_ingredient="")
        self.assertEqual(len(results), 0) # Based on current logic in search_recipes
        results_space = crud.search_recipes(query="  ", filter_ingredient="  ")
        self.assertEqual(len(results_space), 0)
