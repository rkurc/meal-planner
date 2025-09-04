import unittest
import uuid
import json

from meal_planner_app.main import app
from meal_planner_app import crud


class ShoppingListApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()
        # Assuming a new function to reset shopping lists will be created in crud.py
        if hasattr(crud, "reset_shopping_lists_db"):
            crud.reset_shopping_lists_db()

        # --- Create prerequisite data ---
        # 1. Create a recipe with ingredients
        self.recipe1 = crud.create_recipe(
            name="Spaghetti Carbonara",
            instructions="Cook pasta, mix with eggs, cheese, and pancetta.",
            ingredients_data=[
                {"name": "Spaghetti", "quantity": "200", "unit": "g"},
                {"name": "Pancetta", "quantity": "100", "unit": "g"},
                {"name": "Eggs", "quantity": "2", "unit": ""},
            ],
        )
        # 2. Create a meal plan and add the recipe to it
        self.meal_plan = crud.create_meal_plan(
            name="Italian Night", recipe_ids=[self.recipe1.recipe_id]
        )

    def tearDown(self):
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()
        if hasattr(crud, "reset_shopping_lists_db"):
            crud.reset_shopping_lists_db()

    def test_create_and_get_shopping_list(self):
        """
        Test creating a new shopping list from a meal plan and then fetching it.
        """
        # POST to create a shopping list from our meal plan
        response = self.client.post(
            "/api/shopping-lists",
            content_type="application/json",
            data=json.dumps({"meal_plan_id": str(self.meal_plan.meal_plan_id)}),
        )
        self.assertEqual(response.status_code, 201)
        created_data = response.get_json()
        self.assertIn("id", created_data)
        self.assertIn("name", created_data)
        self.assertEqual(f"Shopping List for {self.meal_plan.name}", created_data["name"])
        self.assertIn("items", created_data)
        self.assertEqual(len(created_data["items"]), 3)

        shopping_list_id = created_data["id"]

        # GET the created shopping list by its ID
        response = self.client.get(f"/api/shopping-lists/{shopping_list_id}")
        self.assertEqual(response.status_code, 200)
        get_data = response.get_json()
        self.assertEqual(created_data, get_data)
        self.assertEqual(len(get_data["items"]), 3)
        # Check if an item's 'purchased' status is False by default
        self.assertFalse(get_data["items"][0]["purchased"])

    def test_list_shopping_lists(self):
        """
        Test listing all created shopping lists.
        """
        # Create one shopping list
        self.client.post(
            "/api/shopping-lists",
            content_type="application/json",
            data=json.dumps({"meal_plan_id": str(self.meal_plan.meal_plan_id)}),
        )

        # GET all shopping lists
        response = self.client.get("/api/shopping-lists")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(f"Shopping List for {self.meal_plan.name}", data[0]["name"])

    def test_update_shopping_list(self):
        """
        Test updating a shopping list, e.g., marking an item as purchased.
        """
        # 1. Create the shopping list
        post_response = self.client.post(
            "/api/shopping-lists",
            content_type="application/json",
            data=json.dumps({"meal_plan_id": str(self.meal_plan.meal_plan_id)}),
        )
        self.assertEqual(post_response.status_code, 201)
        shopping_list = post_response.get_json()
        shopping_list_id = shopping_list["id"]
        self.assertFalse(shopping_list["items"][0]["purchased"])

        # 2. Update the first item to be 'purchased'
        shopping_list["items"][0]["purchased"] = True
        put_response = self.client.put(
            f"/api/shopping-lists/{shopping_list_id}",
            content_type="application/json",
            data=json.dumps(shopping_list),
        )
        self.assertEqual(put_response.status_code, 200)
        updated_list = put_response.get_json()
        self.assertTrue(updated_list["items"][0]["purchased"])
        # Ensure other items were not changed
        self.assertFalse(updated_list["items"][1]["purchased"])

    def test_delete_shopping_list(self):
        """
        Test deleting a shopping list.
        """
        # 1. Create the shopping list
        post_response = self.client.post(
            "/api/shopping-lists",
            content_type="application/json",
            data=json.dumps({"meal_plan_id": str(self.meal_plan.meal_plan_id)}),
        )
        self.assertEqual(post_response.status_code, 201)
        shopping_list_id = post_response.get_json()["id"]

        # 2. Delete the shopping list
        delete_response = self.client.delete(f"/api/shopping-lists/{shopping_list_id}")
        self.assertEqual(delete_response.status_code, 204)

        # 3. Verify it's gone
        get_response = self.client.get(f"/api/shopping-lists/{shopping_list_id}")
        self.assertEqual(get_response.status_code, 404)

    def test_create_shopping_list_with_invalid_meal_plan_id(self):
        """
        Test creating a shopping list with a non-existent meal plan ID.
        """
        invalid_id = uuid.uuid4()
        response = self.client.post(
            "/api/shopping-lists",
            content_type="application/json",
            data=json.dumps({"meal_plan_id": str(invalid_id)}),
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
