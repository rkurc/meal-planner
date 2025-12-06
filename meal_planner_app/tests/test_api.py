"""
Tests for the Flask API endpoints and Jinja2 form routes.
"""

import unittest
import json
import uuid
from meal_planner_app.main import app
from meal_planner_app import crud
from meal_planner_app.models.ingredient import Ingredient


class TestApi(unittest.TestCase):
    """Tests for the main API and form routes."""

    def setUp(self):
        """Set up a test client and initialize the database."""
        self.client = app.test_client()
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()

    def tearDown(self):
        """Clean up the database after each test."""
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()

    def test_get_recipes_api(self):
        """Test the GET /api/recipes endpoint."""
        crud.create_recipe(name="API Test Recipe", instructions="Test instructions")

        response = self.client.get("/api/recipes")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "API Test Recipe")
        self.assertIn("ingredients", data[0])  # Check that the full dict is returned

    def test_create_recipe_api(self):
        """Test the POST /api/recipes endpoint."""
        recipe_data = {
            "name": "API Recipe",
            "instructions": "API instructions",
            "description": "API description",
            "source_url": "http://example.com",
            "ingredients": [
                {"name": "Sugar", "quantity": 1, "unit": "cup"},
                {"name": "Spice", "quantity": 1, "unit": "tsp"},
            ],
        }
        response = self.client.post("/api/recipes", json=recipe_data)

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

        # Check that the returned data matches the sent data (ignoring id)
        self.assertEqual(data["name"], recipe_data["name"])
        self.assertEqual(data["instructions"], recipe_data["instructions"])
        self.assertEqual(data["description"], recipe_data["description"])
        self.assertEqual(data["source_url"], recipe_data["source_url"])
        self.assertEqual(len(data["ingredients"]), 2)
        self.assertEqual(data["ingredients"][0]["name"], "Sugar")

        # Check that the recipe was actually created in the DB
        recipes = crud.list_recipes()
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0].name, "API Recipe")
        self.assertEqual(len(recipes[0].ingredients), 2)

        # Check that a subsequent GET request returns the new recipe
        response = self.client.get("/api/recipes")
        self.assertEqual(response.status_code, 200)
        get_data = json.loads(response.data)
        self.assertEqual(len(get_data), 1)
        self.assertEqual(get_data[0]["name"], "API Recipe")

    def test_create_recipe_via_form(self):
        """Test creating a recipe via the Jinja2 form POST."""
        response = self.client.post(
            "/recipes/new",
            data={
                "name": "Form Recipe",
                "instructions": "Form instructions",
                "ingredients-0-name": "Flour",
                "ingredients-0-quantity": "2",
                "ingredients-0-unit": "cups",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b">Recipes</h1>", response.data)
        self.assertIn(b"Form Recipe", response.data)
        recipes = crud.list_recipes()
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0].name, "Form Recipe")

    def test_edit_recipe_via_form(self):
        """Test editing a recipe via the Jinja2 form POST."""
        recipe = crud.create_recipe(
            name="Original Name", instructions="Original instructions"
        )
        response = self.client.post(
            f"/recipes/{recipe.recipe_id}/edit",
            data={
                "name": "Updated Name",
                "instructions": "Updated instructions",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b">Updated Name</h1>", response.data)
        updated_recipe = crud.get_recipe(recipe.recipe_id)
        self.assertEqual(updated_recipe.name, "Updated Name")

    def test_delete_recipe_via_form(self):
        """Test deleting a recipe via the Jinja2 form POST."""
        recipe = crud.create_recipe(name="To Be Deleted", instructions="...")
        response = self.client.post(
            f"/recipes/{recipe.recipe_id}/delete", follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b">Recipes</h1>", response.data)
        self.assertNotIn(b"To Be Deleted", response.data)
        self.assertEqual(len(crud.list_recipes()), 0)

    def test_create_meal_plan_via_form(self):
        """Test creating a meal plan via the Jinja2 form."""
        crud.create_recipe(name="Recipe 1", instructions="...")
        response = self.client.post(
            "/meal-plans/new",
            data={
                "name": "My Weekly Plan",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        # We are redirected to the list page, so we check for the title of that page
        self.assertIn(b">Meal Plans</h1>", response.data)
        # And that the new plan's name is in the body
        self.assertIn(b"My Weekly Plan", response.data)
        meal_plans = crud.list_meal_plans()
        self.assertEqual(len(meal_plans), 1)
        self.assertEqual(meal_plans[0].name, "My Weekly Plan")

    def test_generate_shopping_list_route(self):
        """Test the shopping list generation route."""
        recipe = crud.create_recipe(
            name="Test Soup",
            instructions="Boil it.",
            ingredients_data=[{"name": "Carrot", "quantity": 2, "unit": "pcs"}],
        )
        mp = crud.create_meal_plan(name="Soup Plan")
        crud.add_recipe_to_meal_plan(mp.meal_plan_id, recipe.recipe_id)

        response = self.client.get(f"/meal-plans/{mp.meal_plan_id}/shopping-list")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>Shopping List for "Soup Plan"</h1>', response.data)
        self.assertIn(b"Carrot", response.data)

    def test_get_recipe_by_id_api(self):
        """Test GET /api/recipes/<id> endpoint."""
        recipe = crud.create_recipe(
            name="Test Recipe",
            instructions="Test instructions",
            description="Test description",
            source_url="http://example.com",
            ingredients_data=[
                {"name": "Sugar", "quantity": 1, "unit": "cup"},
                {"name": "Flour", "quantity": 2, "unit": "cups"},
            ],
        )

        response = self.client.get(f"/api/recipes/{recipe.recipe_id}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "Test Recipe")
        self.assertEqual(data["instructions"], "Test instructions")
        self.assertEqual(data["description"], "Test description")
        self.assertEqual(data["source_url"], "http://example.com")
        self.assertEqual(len(data["ingredients"]), 2)
        self.assertEqual(data["ingredients"][0]["name"], "Sugar")

    def test_get_recipe_by_id_not_found(self):
        """Test GET /api/recipes/<id> with non-existent recipe."""
        non_existent_id = uuid.uuid4()
        response = self.client.get(f"/api/recipes/{non_existent_id}")
        self.assertEqual(response.status_code, 404)

    def test_update_recipe_api(self):
        """Test PUT /api/recipes/<id> endpoint."""
        recipe = crud.create_recipe(
            name="Original Recipe",
            instructions="Original instructions",
            ingredients_data=[{"name": "Sugar", "quantity": 1, "unit": "cup"}],
        )

        update_data = {
            "name": "Updated Recipe",
            "instructions": "Updated instructions",
            "description": "Updated description",
            "source_url": "http://updated.com",
            "ingredients": [
                {"name": "Flour", "quantity": 3, "unit": "cups"},
                {"name": "Water", "quantity": 200, "unit": "ml"},
            ],
        }

        response = self.client.put(f"/api/recipes/{recipe.recipe_id}", json=update_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "Updated Recipe")
        self.assertEqual(data["instructions"], "Updated instructions")
        self.assertEqual(data["description"], "Updated description")
        self.assertEqual(len(data["ingredients"]), 2)
        self.assertEqual(data["ingredients"][0]["name"], "Flour")

        # Verify changes in DB
        updated_recipe = crud.get_recipe(recipe.recipe_id)
        self.assertEqual(updated_recipe.name, "Updated Recipe")
        self.assertEqual(len(updated_recipe.ingredients), 2)

    def test_update_recipe_not_found(self):
        """Test PUT /api/recipes/<id> with non-existent recipe."""
        non_existent_id = uuid.uuid4()
        update_data = {"name": "Updated Name", "instructions": "Updated instructions"}
        response = self.client.put(f"/api/recipes/{non_existent_id}", json=update_data)
        self.assertEqual(response.status_code, 404)

    def test_delete_recipe_api(self):
        """Test DELETE /api/recipes/<id> endpoint."""
        recipe = crud.create_recipe(name="To Be Deleted", instructions="...")
        recipe_id = recipe.recipe_id

        response = self.client.delete(f"/api/recipes/{recipe_id}")
        self.assertEqual(response.status_code, 204)

        # Verify recipe is deleted
        self.assertIsNone(crud.get_recipe(recipe_id))
        self.assertEqual(len(crud.list_recipes()), 0)

    def test_delete_recipe_not_found(self):
        """Test DELETE /api/recipes/<id> with non-existent recipe."""
        non_existent_id = uuid.uuid4()
        response = self.client.delete(f"/api/recipes/{non_existent_id}")
        self.assertEqual(response.status_code, 404)


class TestMealPlanApi(unittest.TestCase):
    """Tests specifically for the Meal Plan API endpoints."""

    def setUp(self):
        """Set up a test client and initialize the database."""
        self.client = app.test_client()
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()
        self.recipe1 = crud.create_recipe(name="R1", instructions="I1")
        self.recipe2 = crud.create_recipe(name="R2", instructions="I2")

    def tearDown(self):
        """Clean up the database after each test."""
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()

    def test_get_meal_plans_api_empty(self):
        """Test GET /api/meal-plans when no meal plans exist."""
        response = self.client.get("/api/meal-plans")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])

    def test_create_meal_plan_api(self):
        """Test POST /api/meal-plans to create a new meal plan."""
        response = self.client.post(
            "/api/meal-plans",
            json={
                "name": "New API Plan",
                "description": "A plan for the new API.",
                "recipe_ids": [str(self.recipe1.recipe_id)],
            },
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "New API Plan")
        self.assertEqual(data["description"], "A plan for the new API.")
        self.assertIn(str(self.recipe1.recipe_id), data["recipe_ids"])
        self.assertIn("id", data)

        # Verify it was actually created
        mp = crud.get_meal_plan(uuid.UUID(data["id"]))
        self.assertIsNotNone(mp)
        self.assertEqual(mp.name, "New API Plan")
        self.assertEqual(mp.description, "A plan for the new API.")

    def test_get_meal_plan_by_id_api(self):
        """Test GET /api/meal-plans/<id>."""
        mp = crud.create_meal_plan(
            name="Test Plan",
            description="Test Description",
            recipe_ids=[self.recipe1.recipe_id],
        )
        response = self.client.get(f"/api/meal-plans/{mp.meal_plan_id}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "Test Plan")
        self.assertEqual(data["description"], "Test Description")
        self.assertEqual(data["id"], str(mp.meal_plan_id))
        self.assertEqual(data["recipe_ids"], [str(self.recipe1.recipe_id)])

    def test_update_meal_plan_api(self):
        """Test PUT /api/meal-plans/<id>."""
        mp = crud.create_meal_plan(
            name="Old Name",
            description="Old Description",
            recipe_ids=[self.recipe1.recipe_id],
        )
        update_data = {
            "name": "New Name",
            "description": "New Description",
            "recipe_ids": [str(self.recipe2.recipe_id)],
        }
        response = self.client.put(
            f"/api/meal-plans/{mp.meal_plan_id}", json=update_data
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "New Name")
        self.assertEqual(data["description"], "New Description")
        self.assertEqual(data["recipe_ids"], [str(self.recipe2.recipe_id)])

        # Verify changes in DB
        updated_mp = crud.get_meal_plan(mp.meal_plan_id)
        self.assertEqual(updated_mp.name, "New Name")
        self.assertEqual(updated_mp.description, "New Description")
        self.assertNotIn(self.recipe1.recipe_id, updated_mp.recipe_ids)
        self.assertIn(self.recipe2.recipe_id, updated_mp.recipe_ids)

    def test_delete_meal_plan_api(self):
        """Test DELETE /api/meal-plans/<id>."""
        mp = crud.create_meal_plan(name="To Delete")
        response = self.client.delete(f"/api/meal-plans/{mp.meal_plan_id}")
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(crud.get_meal_plan(mp.meal_plan_id))

    def test_add_recipe_to_meal_plan_api(self):
        """Test POST /api/meal-plans/<id>/recipes."""
        mp = crud.create_meal_plan(name="My Plan")
        response = self.client.post(
            f"/api/meal-plans/{mp.meal_plan_id}/recipes",
            json={"recipe_id": str(self.recipe1.recipe_id)},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn(str(self.recipe1.recipe_id), data["recipe_ids"])

    def test_remove_recipe_from_meal_plan_api(self):
        """Test DELETE /api/meal-plans/<id>/recipes/<recipe_id>."""
        mp = crud.create_meal_plan(
            name="My Plan", recipe_ids=[self.recipe1.recipe_id, self.recipe2.recipe_id]
        )
        response = self.client.delete(
            f"/api/meal-plans/{mp.meal_plan_id}/recipes/{self.recipe1.recipe_id}"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertNotIn(str(self.recipe1.recipe_id), data["recipe_ids"])
        self.assertIn(str(self.recipe2.recipe_id), data["recipe_ids"])

    def test_get_shopping_list_api(self):
        """Test GET /api/meal-plans/<id>/shopping-list."""
        # Setup: recipe1 has 1 egg, recipe2 has 3 eggs.
        self.recipe1.ingredients.append(Ingredient(name="Egg", quantity=1, unit="pc"))
        self.recipe2.ingredients.append(Ingredient(name="Egg", quantity=3, unit="pc"))
        self.recipe2.ingredients.append(
            Ingredient(name="Flour", quantity=200, unit="g")
        )

        mp = crud.create_meal_plan(
            name="Test Shopping List Plan",
            recipe_ids=[self.recipe1.recipe_id, self.recipe2.recipe_id],
        )

        response = self.client.get(f"/api/meal-plans/{mp.meal_plan_id}/shopping-list")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIsInstance(data, list)

        # Find the 'Egg' ingredient in the shopping list
        egg_item = next((item for item in data if item["name"] == "Egg"), None)
        self.assertIsNotNone(egg_item)
        self.assertEqual(egg_item["quantity"], 4)  # 1 + 3
        self.assertEqual(egg_item["unit"], "pc")

        # Find the 'Flour' ingredient
        flour_item = next((item for item in data if item["name"] == "Flour"), None)
        self.assertIsNotNone(flour_item)
        self.assertEqual(flour_item["quantity"], 200)
        self.assertEqual(flour_item["unit"], "g")


if __name__ == "__main__":
    unittest.main()
