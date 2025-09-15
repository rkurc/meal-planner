import json
from .base import BaseTestCase
from meal_planner_app import crud, db


class ShoppingListApiTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        # --- Create prerequisite data ---
        self.recipe1 = crud.create_recipe(
            name="Spaghetti Carbonara",
            instructions="Cook pasta, mix with eggs, cheese, and pancetta.",
            ingredients_data=[
                {"name": "Spaghetti", "quantity": "200", "unit": "g"},
                {"name": "Pancetta", "quantity": "100", "unit": "g"},
                {"name": "Eggs", "quantity": "2", "unit": ""},
            ],
        )
        self.meal_plan = crud.create_meal_plan(
            name="Italian Night", recipe_ids=[self.recipe1.id]
        )
        db.session.commit()

    def test_create_and_get_shopping_list(self):
        """
        Test creating a new shopping list from a meal plan and then fetching it.
        """
        response = self.client.post(
            "/api/shopping-lists",
            content_type="application/json",
            data=json.dumps({"meal_plan_id": str(self.meal_plan.id)}),
        )
        self.assertEqual(response.status_code, 201)
