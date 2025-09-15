"""
Base test case for the application.
"""

import unittest
from meal_planner_app import create_app, db


class BaseTestCase(unittest.TestCase):
    """A base test case for the meal planner app."""

    def setUp(self):
        """Set up a test client and initialize the database."""
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "WTF_CSRF_ENABLED": False,
            }
        )
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up the database after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
