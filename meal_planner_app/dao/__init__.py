"""Persistence DAOs. Application code should depend on protocols, not sqlite.py."""

from meal_planner_app.dao.factory import create_dao
from meal_planner_app.dao.protocol import MealPlannerDao

__all__ = ["create_dao", "MealPlannerDao"]
