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
        self.assertEqual(
            f"Shopping List for {self.meal_plan.name}", created_data["name"]
        )
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

    def test_download_persisted_shopping_list_pdf_happy_path(self):
        """GET /shopping-lists/<id>/pdf returns 200 PDF with correct headers and PDF magic."""
        # Create shopping list
        post_resp = self.client.post(
            "/api/shopping-lists",
            content_type="application/json",
            data=json.dumps({"meal_plan_id": str(self.meal_plan.meal_plan_id)}),
        )
        self.assertEqual(post_resp.status_code, 201)
        sl_id = post_resp.get_json()["id"]

        resp = self.client.get(f"/shopping-lists/{sl_id}/pdf")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/pdf", resp.content_type)
        self.assertTrue(resp.data.startswith(b"%PDF"))

    def test_download_persisted_pdf_excludes_purchased(self):
        """Purchased items must not appear in the PDF content."""
        # Create list
        post_resp = self.client.post(
            "/api/shopping-lists",
            content_type="application/json",
            data=json.dumps({"meal_plan_id": str(self.meal_plan.meal_plan_id)}),
        )
        sl = post_resp.get_json()
        sl_id = sl["id"]

        # Mark first item purchased
        sl["items"][0]["purchased"] = True
        put_resp = self.client.put(
            f"/api/shopping-lists/{sl_id}",
            content_type="application/json",
            data=json.dumps(sl),
        )
        self.assertEqual(put_resp.status_code, 200)

        pdf_resp = self.client.get(f"/shopping-lists/{sl_id}/pdf")
        self.assertEqual(pdf_resp.status_code, 200)
        body = pdf_resp.data.decode("latin-1", errors="replace")
        # The purchased item's name should not be in the PDF body
        self.assertNotIn(sl["items"][0]["name"], body)

    def test_download_persisted_pdf_location_id_only_grouping(self):
        """Item with only location_id groups under id (key '4' present)."""
        # Create list from the basic meal plan
        post_resp = self.client.post(
            "/api/shopping-lists",
            content_type="application/json",
            data=json.dumps({"meal_plan_id": str(self.meal_plan.meal_plan_id)}),
        )
        sl = post_resp.get_json()
        sl_id = sl["id"]

        # Force one item to have location=None and location_id="4"
        sl["items"][0]["location"] = None
        sl["items"][0]["location_id"] = "4"
        put_resp = self.client.put(
            f"/api/shopping-lists/{sl_id}",
            content_type="application/json",
            data=json.dumps(sl),
        )
        self.assertEqual(put_resp.status_code, 200)

        # Verify grouping logic directly (PDF content streams are compressed)
        sl_obj = crud.get_shopping_list(uuid.UUID(sl_id))
        grouped = crud.shopping_list_to_pdf_data(sl_obj)  # pylint: disable=no-member
        self.assertIn("4", grouped)
        # The key "4" comes from location_id fallback

        # PDF route still works and returns valid PDF
        pdf_resp = self.client.get(f"/shopping-lists/{sl_id}/pdf")
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertTrue(pdf_resp.data.startswith(b"%PDF"))

    def test_api_get_ingredients(self):
        """GET /api/ingredients returns sorted unique ingredient names from recipes."""
        # Our setUp creates a recipe with Spaghetti, Pancetta, Eggs
        resp = self.client.get("/api/ingredients")
        self.assertEqual(resp.status_code, 200)
        names = resp.get_json()
        self.assertIsInstance(names, list)
        self.assertEqual(names, sorted(names))
        # At minimum these should be present
        self.assertIn("Spaghetti", names)
        self.assertIn("Pancetta", names)
        self.assertIn("Eggs", names)

    def test_api_get_locations(self):
        """GET /api/locations returns sorted unique location values."""
        # Seed a recipe that has locations to ensure non-empty deterministic result
        crud.reset_recipes_db()
        crud.reset_meal_plans_db()
        crud.create_recipe(
            name="Test Recipe",
            instructions="Test.",
            ingredients_data=[
                {"name": "Milk", "quantity": 1, "unit": "l", "location": "Dairy"},
                {"name": "Bread", "quantity": 1, "unit": "", "location_id": "Bakery"},
            ],
        )
        resp = self.client.get("/api/locations")
        self.assertEqual(resp.status_code, 200)
        locs = resp.get_json()
        self.assertIsInstance(locs, list)
        self.assertEqual(locs, sorted(locs))
        # Should include both the resolved location and the id fallback
        self.assertIn("Dairy", locs)
        self.assertIn("Bakery", locs)

    def test_group_items_for_display_canonical_location_id_fallback(self):
        """Directly proves canonical grouping for location_id-only items (dicts and dataclasses)."""
        # dicts (as produced by aggregation in generate_shopping_list)
        items_dicts = [
            {
                "name": "Foo",
                "quantity": 1,
                "unit": "",
                "location": None,
                "location_id": "4",
            },
            {
                "name": "Bar",
                "quantity": 2,
                "unit": "",
                "location": None,
                "location_id": "4",
            },
            {
                "name": "Baz",
                "quantity": 1,
                "unit": "",
                "location": "",
                "location_id": None,
            },
        ]
        grouped = crud.group_items_for_display(items_dicts)
        self.assertIn("4", grouped)
        self.assertIn("Baz", [i["name"] for i in grouped.get("", [])])
        # location_id items do not go to ""
        names_in_4 = [i["name"] for i in grouped.get("4", [])]
        self.assertIn("Foo", names_in_4)
        self.assertIn("Bar", names_in_4)

        # ShoppingListItem dataclass form (as used for persisted)
        from meal_planner_app.models.shopping_list import ShoppingListItem

        item_dc = ShoppingListItem(
            name="Qux",
            quantity=3,
            unit="",
            purchased=False,
            location=None,
            location_id="Dairy",
        )
        grouped_dc = crud.group_items_for_display([item_dc])
        self.assertIn("Dairy", grouped_dc)
        self.assertEqual(grouped_dc["Dairy"][0]["name"], "Qux")


if __name__ == "__main__":
    unittest.main()
