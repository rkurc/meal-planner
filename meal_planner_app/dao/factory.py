"""Build a MealPlannerDao. Swap this module to change backends later."""

import os
from typing import Optional

from meal_planner_app.dao.protocol import MealPlannerDao
from meal_planner_app.dao.sqlite import SqliteDao


def create_dao(path: Optional[str] = None) -> MealPlannerDao:
    """Return the SQLite DAO. path defaults to MEAL_PLANNER_DB or data/meal_planner.db."""
    if path is None:
        path = os.environ.get("MEAL_PLANNER_DB") or "data/meal_planner.db"
    return SqliteDao(path)
