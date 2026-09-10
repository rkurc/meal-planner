"""Process-wide DAO accessor used by domain modules."""

from typing import Optional

from meal_planner_app.dao.factory import create_dao
from meal_planner_app.dao.protocol import MealPlannerDao

_dao: Optional[MealPlannerDao] = None


def set_dao(dao: Optional[MealPlannerDao]) -> None:
    """Install (or clear) the process-wide DAO. Tests pass an in-memory instance."""
    # pylint: disable=global-statement
    global _dao
    _dao = dao


def get_dao() -> MealPlannerDao:
    """Lazy default: MEAL_PLANNER_DB or data/meal_planner.db."""
    # pylint: disable=global-statement
    global _dao
    if _dao is None:
        _dao = create_dao()
    return _dao
