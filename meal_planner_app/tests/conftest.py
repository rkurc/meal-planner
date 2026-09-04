"""Use an in-memory SQLite DAO for every test."""

import pytest

from meal_planner_app import crud
from meal_planner_app.dao.factory import create_dao


@pytest.fixture(autouse=True)
def _memory_dao():
    dao = create_dao(":memory:")
    crud.set_dao(dao)
    yield dao
    dao.close()
    crud.set_dao(None)
