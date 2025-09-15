"""
Tests for the Flask API endpoints, now using a test database.
"""

import json
from .base import BaseTestCase
from meal_planner_app import crud


class TestApi(BaseTestCase):
    """Tests for the main API and form routes."""

    def test_get_recipes_api(self):
        """Test the GET /api/recipes endpoint."""
        crud.create_recipe(name="API Test Recipe", instructions="Test instructions")

        response = self.client.get("/api/recipes")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "API Test Recipe")
