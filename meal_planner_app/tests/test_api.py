import unittest
import json
import uuid
from meal_planner_app.main import app
from meal_planner_app import crud
from meal_planner_app.models.ingredient import Ingredient

class TestApi(unittest.TestCase):

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

        response = self.client.get('/api/recipes')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "API Test Recipe")

    def test_create_recipe_via_form(self):
        """Test creating a recipe via the Jinja2 form POST."""
        response = self.client.post('/recipes/new', data={
            'name': 'Form Recipe',
            'instructions': 'Form instructions',
            'ingredients-0-name': 'Flour',
            'ingredients-0-quantity': '2',
            'ingredients-0-unit': 'cups',
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'>Recipes</h1>', response.data)
        self.assertIn(b'Form Recipe', response.data)
        recipes = crud.list_recipes()
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0].name, 'Form Recipe')

    def test_edit_recipe_via_form(self):
        """Test editing a recipe via the Jinja2 form POST."""
        recipe = crud.create_recipe(name="Original Name", instructions="Original instructions")
        response = self.client.post(f'/recipes/{recipe.id}/edit', data={
            'name': 'Updated Name',
            'instructions': 'Updated instructions',
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'>Updated Name</h1>', response.data)
        updated_recipe = crud.get_recipe(recipe.id)
        self.assertEqual(updated_recipe.name, 'Updated Name')

    def test_delete_recipe_via_form(self):
        """Test deleting a recipe via the Jinja2 form POST."""
        recipe = crud.create_recipe(name="To Be Deleted", instructions="...")
        response = self.client.post(f'/recipes/{recipe.id}/delete', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'>Recipes</h1>', response.data)
        self.assertNotIn(b'To Be Deleted', response.data)
        self.assertEqual(len(crud.list_recipes()), 0)

    def test_create_meal_plan_via_form(self):
        """Test creating a meal plan via the Jinja2 form."""
        recipe1 = crud.create_recipe(name="Recipe 1", instructions="...")
        response = self.client.post('/meal-plans/new', data={
            'name': 'My Weekly Plan',
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # We are redirected to the list page, so we check for the title of that page
        self.assertIn(b'>Meal Plans</h1>', response.data)
        # And that the new plan's name is in the body
        self.assertIn(b'My Weekly Plan', response.data)
        meal_plans = crud.list_meal_plans()
        self.assertEqual(len(meal_plans), 1)
        self.assertEqual(meal_plans[0].name, 'My Weekly Plan')

    def test_generate_shopping_list_route(self):
        """Test the shopping list generation route."""
        recipe = crud.create_recipe(name="Test Soup", instructions="Boil it.", ingredients_data=[
            {'name': 'Carrot', 'quantity': 2, 'unit': 'pcs'}])
        mp = crud.create_meal_plan(name="Soup Plan")
        crud.add_recipe_to_meal_plan(mp.id, recipe.id)

        response = self.client.get(f'/meal-plans/{mp.id}/shopping-list')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>Shopping List for "Soup Plan"</h1>', response.data)
        self.assertIn(b'Carrot', response.data)

class TestMealPlanApi(unittest.TestCase):

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
        response = self.client.get('/api/meal-plans')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])

    def test_create_meal_plan_api(self):
        """Test POST /api/meal-plans to create a new meal plan."""
        response = self.client.post('/api/meal-plans',
                                    json={'name': 'New API Plan', 'recipe_ids': [str(self.recipe1.id)]})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'New API Plan')
        self.assertIn(str(self.recipe1.id), data['recipe_ids'])
        self.assertIn('id', data)

        # Verify it was actually created
        mp = crud.get_meal_plan(uuid.UUID(data['id']))
        self.assertIsNotNone(mp)
        self.assertEqual(mp.name, 'New API Plan')

    def test_get_meal_plan_by_id_api(self):
        """Test GET /api/meal-plans/<id>."""
        mp = crud.create_meal_plan(name="Test Plan", recipe_ids=[self.recipe1.id])
        response = self.client.get(f'/api/meal-plans/{mp.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Test Plan')
        self.assertEqual(data['id'], str(mp.id))
        self.assertEqual(data['recipe_ids'], [str(self.recipe1.id)])

    def test_update_meal_plan_api(self):
        """Test PUT /api/meal-plans/<id>."""
        mp = crud.create_meal_plan(name="Old Name", recipe_ids=[self.recipe1.id])
        update_data = {
            'name': 'New Name',
            'recipe_ids': [str(self.recipe2.id)]
        }
        response = self.client.put(f'/api/meal-plans/{mp.id}', json=update_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'New Name')
        self.assertEqual(data['recipe_ids'], [str(self.recipe2.id)])

        # Verify changes in DB
        updated_mp = crud.get_meal_plan(mp.id)
        self.assertEqual(updated_mp.name, 'New Name')
        self.assertNotIn(self.recipe1.id, updated_mp.recipe_ids)
        self.assertIn(self.recipe2.id, updated_mp.recipe_ids)

    def test_delete_meal_plan_api(self):
        """Test DELETE /api/meal-plans/<id>."""
        mp = crud.create_meal_plan(name="To Delete")
        response = self.client.delete(f'/api/meal-plans/{mp.id}')
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(crud.get_meal_plan(mp.id))

    def test_add_recipe_to_meal_plan_api(self):
        """Test POST /api/meal-plans/<id>/recipes."""
        mp = crud.create_meal_plan(name="My Plan")
        response = self.client.post(f'/api/meal-plans/{mp.id}/recipes', json={'recipe_id': str(self.recipe1.id)})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn(str(self.recipe1.id), data['recipe_ids'])

    def test_remove_recipe_from_meal_plan_api(self):
        """Test DELETE /api/meal-plans/<id>/recipes/<recipe_id>."""
        mp = crud.create_meal_plan(name="My Plan", recipe_ids=[self.recipe1.id, self.recipe2.id])
        response = self.client.delete(f'/api/meal-plans/{mp.id}/recipes/{self.recipe1.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertNotIn(str(self.recipe1.id), data['recipe_ids'])
        self.assertIn(str(self.recipe2.id), data['recipe_ids'])

    def test_get_shopping_list_api(self):
        """Test GET /api/meal-plans/<id>/shopping-list."""
        # Setup: recipe1 has 1 egg, recipe2 has 3 eggs.
        self.recipe1.ingredients.append(Ingredient(name="Egg", quantity=1, unit="pc"))
        self.recipe2.ingredients.append(Ingredient(name="Egg", quantity=3, unit="pc"))
        self.recipe2.ingredients.append(Ingredient(name="Flour", quantity=200, unit="g"))

        mp = crud.create_meal_plan(name="Test Shopping List Plan", recipe_ids=[self.recipe1.id, self.recipe2.id])

        response = self.client.get(f'/api/meal-plans/{mp.id}/shopping-list')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIsInstance(data, list)

        # Find the 'Egg' ingredient in the shopping list
        egg_item = next((item for item in data if item['name'] == 'Egg'), None)
        self.assertIsNotNone(egg_item)
        self.assertEqual(egg_item['quantity'], 4) # 1 + 3
        self.assertEqual(egg_item['unit'], 'pc')

        # Find the 'Flour' ingredient
        flour_item = next((item for item in data if item['name'] == 'Flour'), None)
        self.assertIsNotNone(flour_item)
        self.assertEqual(flour_item['quantity'], 200)
        self.assertEqual(flour_item['unit'], 'g')


if __name__ == '__main__':
    unittest.main()
