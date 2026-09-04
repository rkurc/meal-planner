# Persistent SQLite DAO Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist recipes, master ingredients, meal plans, and shopping lists in a SQLite file behind nested DAOs, without changing the Flask JSON API.

**Architecture:** `crud.py` keeps its public functions and calls `MealPlannerDao`. SQL lives only in `SqliteDao`. Master `ingredients` table is created first; recipe lines FK to it. Domain models stay plain Python.

**Tech Stack:** Python 3.9, stdlib `sqlite3`, Flask, pytest, Docker `meal-planner:dev`.

**Spec:** `docs/superpowers/specs/2026-09-04-persistent-sqlite-dao-design.md`

---

## File map

| File | Role |
|---|---|
| `meal_planner_app/models/ingredient.py` | Add `MasterIngredient`; optional `ingredient_id` on `Ingredient` |
| `meal_planner_app/dao/protocol.py` | Entity Protocols + `MealPlannerDao` |
| `meal_planner_app/dao/sqlite.py` | Schema + nested sqlite DAOs |
| `meal_planner_app/dao/factory.py` | `create_dao(path)` |
| `meal_planner_app/dao/__init__.py` | Re-exports |
| `meal_planner_app/crud.py` | Replace in-memory lists with DAO calls |
| `meal_planner_app/seed_db.py` | Add `seed_if_empty` |
| `meal_planner_app/tests/conftest.py` | Autouse in-memory DAO |
| `meal_planner_app/tests/test_dao.py` | DAO tests (TDD) |
| `start_and_seed.sh` | Call `seed_if_empty` |
| `Dockerfile` | `/app/data`, `MEAL_PLANNER_DB` |
| `.gitignore` / `.dockerignore` | `*.db` |
| `.ai/next_step.md`, `.ai/progress.md`, `.ai/stack.md` | Status |

Docker tests:

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/test_dao.py -q --tb=short
```

---

### Task 1: MasterIngredient + Ingredient DAO (SQLite)

**Files:**
- Create: `meal_planner_app/dao/protocol.py`, `sqlite.py`, `factory.py`, `__init__.py`
- Modify: `meal_planner_app/models/ingredient.py`
- Test: `meal_planner_app/tests/test_dao.py`

- [ ] **Step 1: Write failing tests** in `test_dao.py` for ingredient insert/find_by_id/find_by_name/find_all/update/delete and delete-restricted-after-recipe (recipe test can wait until Task 2). First batch: no recipes.

```python
"""DAO tests: SQLite adapter behind MealPlannerDao protocols."""

import os
import tempfile
import unittest
import uuid

from meal_planner_app.dao.factory import create_dao
from meal_planner_app.models.ingredient import MasterIngredient


class TestIngredientDao(unittest.TestCase):
    def setUp(self):
        self.dao = create_dao(":memory:")

    def tearDown(self):
        self.dao.close()

    def test_insert_and_find_by_id(self):
        saved = self.dao.ingredients.insert(
            MasterIngredient(name="Flour", default_unit="cups", location="Baking")
        )
        self.assertIsInstance(saved.ingredient_id, uuid.UUID)
        found = self.dao.ingredients.find_by_id(saved.ingredient_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Flour")
        self.assertEqual(found.default_unit, "cups")
        self.assertEqual(found.location, "Baking")

    def test_find_by_name(self):
        self.dao.ingredients.insert(MasterIngredient(name="Milk", default_unit="cups"))
        found = self.dao.ingredients.find_by_name("Milk")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Milk")
        self.assertIsNone(self.dao.ingredients.find_by_name("missing"))

    def test_find_all_sorted_by_name(self):
        self.dao.ingredients.insert(MasterIngredient(name="Salt"))
        self.dao.ingredients.insert(MasterIngredient(name="Eggs"))
        names = [i.name for i in self.dao.ingredients.find_all()]
        self.assertEqual(names, ["Eggs", "Salt"])

    def test_update_and_delete(self):
        saved = self.dao.ingredients.insert(MasterIngredient(name="Butter"))
        saved.default_unit = "tbsp"
        updated = self.dao.ingredients.update(saved)
        self.assertEqual(updated.default_unit, "tbsp")
        self.assertTrue(self.dao.ingredients.delete(saved.ingredient_id))
        self.assertIsNone(self.dao.ingredients.find_by_id(saved.ingredient_id))
        self.assertFalse(self.dao.ingredients.delete(saved.ingredient_id))

    def test_file_persists_across_connections(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            dao = create_dao(path)
            dao.ingredients.insert(MasterIngredient(name="Cheese"))
            dao.close()
            dao2 = create_dao(path)
            found = dao2.ingredients.find_by_name("Cheese")
            self.assertIsNotNone(found)
            dao2.close()
        finally:
            os.remove(path)
```

- [ ] **Step 2: Run tests — expect FAIL** (import error / no `create_dao`)

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/test_dao.py::TestIngredientDao -q --tb=short
```

- [ ] **Step 3: Implement** `MasterIngredient`, protocols, `SqliteDao` schema (all tables now so later tasks do not migrate), ingredient nested DAO, `create_dao`.

`MasterIngredient` in `models/ingredient.py`:

```python
import uuid
from typing import Optional, Union


class MasterIngredient:
    """Catalog ingredient (aisle + default unit). No quantity."""

    def __init__(
        self,
        name: str,
        default_unit: str = "",
        location: Optional[str] = None,
        location_id: Optional[str] = None,
        ingredient_id: Optional[uuid.UUID] = None,
    ):
        self.ingredient_id = ingredient_id if ingredient_id else uuid.uuid4()
        self.name = name
        self.default_unit = default_unit or ""
        self.location = location
        self.location_id = location_id
```

Add optional `ingredient_id=None` to existing `Ingredient.__init__` and store it on `self`.

`protocol.py` as in the spec.

`sqlite.py`: one connection; nested `_SqliteIngredientDao(conn)` with `insert/find_by_id/find_by_name/find_all/update/delete`. Schema from the spec. Quantity helpers `_qty_dump` / `_qty_load` using `json`.

`factory.py`:

```python
import os
from meal_planner_app.dao.protocol import MealPlannerDao
from meal_planner_app.dao.sqlite import SqliteDao

def create_dao(path=None) -> MealPlannerDao:
    if path is None:
        path = os.environ.get("MEAL_PLANNER_DB") or "data/meal_planner.db"
    return SqliteDao(path)
```

- [ ] **Step 4: Tests pass** (same pytest command)
- [ ] **Step 5: Commit** `feat: add SQLite ingredient DAO and schema`

---

### Task 2: Recipe DAO

**Files:** Modify `sqlite.py`; test `test_dao.py`

- [ ] **Step 1: Failing tests**

```python
from meal_planner_app.models.ingredient import Ingredient, MasterIngredient
from meal_planner_app.models.recipe import Recipe


class TestRecipeDao(unittest.TestCase):
    def setUp(self):
        self.dao = create_dao(":memory:")
        self.flour = self.dao.ingredients.insert(
            MasterIngredient(name="Flour", default_unit="cups", location="Baking")
        )

    def tearDown(self):
        self.dao.close()

    def test_insert_recipe_with_ingredient_line(self):
        recipe = Recipe(
            name="Pancakes",
            instructions="Mix",
            ingredients=[
                Ingredient(
                    name="Flour",
                    quantity=1.5,
                    unit="cups",
                    location="Baking",
                    ingredient_id=self.flour.ingredient_id,
                )
            ],
        )
        saved = self.dao.recipes.insert(recipe)
        found = self.dao.recipes.find_by_id(saved.recipe_id)
        self.assertEqual(found.name, "Pancakes")
        self.assertEqual(len(found.ingredients), 1)
        self.assertEqual(found.ingredients[0].name, "Flour")
        self.assertEqual(found.ingredients[0].quantity, 1.5)
        self.assertEqual(found.ingredients[0].ingredient_id, self.flour.ingredient_id)

    def test_delete_ingredient_restricted_when_used(self):
        recipe = Recipe(
            name="Pancakes",
            instructions="Mix",
            ingredients=[
                Ingredient(
                    name="Flour",
                    quantity=1,
                    unit="cups",
                    ingredient_id=self.flour.ingredient_id,
                )
            ],
        )
        self.dao.recipes.insert(recipe)
        self.assertFalse(self.dao.ingredients.delete(self.flour.ingredient_id))
        self.assertIsNotNone(self.dao.ingredients.find_by_id(self.flour.ingredient_id))

    def test_delete_recipe_then_ingredient(self):
        recipe = Recipe(
            name="Pancakes",
            instructions="Mix",
            ingredients=[
                Ingredient(
                    name="Flour",
                    quantity=1,
                    unit="cups",
                    ingredient_id=self.flour.ingredient_id,
                )
            ],
        )
        saved = self.dao.recipes.insert(recipe)
        self.assertTrue(self.dao.recipes.delete(saved.recipe_id))
        self.assertTrue(self.dao.ingredients.delete(self.flour.ingredient_id))
```

- [ ] **Step 2: Run — FAIL** until recipe nested DAO exists
- [ ] **Step 3: Implement** `_SqliteRecipeDao`: insert recipe row + `recipe_ingredients`; find joins ingredients ordered by position; update replaces child rows; delete recipe row (cascade). Empty line `unit` → master `default_unit` on read.
- [ ] **Step 4: Tests pass**
- [ ] **Step 5: Commit** `feat: persist recipes linked to master ingredients`

---

### Task 3: Meal plan + shopping list DAOs

**Files:** Modify `sqlite.py`; test `test_dao.py`

- [ ] **Step 1: Failing tests** for meal plan insert with `{recipe_id, count}`, shopping list snapshot items (including list quantity), delete meal plan sets shopping_list.meal_plan_id to None.
- [ ] **Step 2: Run — FAIL**
- [ ] **Step 3: Implement** nested meal plan / shopping list DAOs. Shopping items are snapshots (no ingredient FK).
- [ ] **Step 4: Tests pass**
- [ ] **Step 5: Commit** `feat: persist meal plans and shopping lists`

---

### Task 4: Wire `crud.py`

**Files:** Modify `crud.py`; create `tests/conftest.py`

- [ ] **Step 1: Add autouse memory DAO** so existing tests do not touch a file:

```python
import pytest
from meal_planner_app import crud
from meal_planner_app.dao.factory import create_dao

@pytest.fixture(autouse=True)
def _memory_dao():
    dao = create_dao(":memory:")
    crud.set_dao(dao)
    yield
    dao.close()
    crud.set_dao(None)
```

- [ ] **Step 2: Replace lists** in `crud.py` with `get_dao()`. Keep function signatures. `create_recipe` get-or-creates master ingredients (do not overwrite non-empty default_unit/location). `reset_recipes_db` deletes recipes then ingredients. `reset_meal_plans_db` / `reset_shopping_lists_db` delete those tables. `search_recipes` uses `list_recipes()`. Unique names/locations from `ingredients.find_all()`.
- [ ] **Step 3: Run full pytest** in Docker — all existing tests green plus DAO tests.
- [ ] **Step 4: Commit** `feat: back crud.py with SQLite DAO`

---

### Task 5: Seed-if-empty + Docker path

**Files:** `seed_db.py`, `start_and_seed.sh`, `Dockerfile`, `.gitignore`, `.dockerignore`

- [ ] **Step 1:** `seed_if_empty()` — if `list_recipes()`: return; else insert `RECIPES_TO_SEED` + `seed_meal_plans()` (no reset). `seed_database()` still resets (E2E).
- [ ] **Step 2:** `start_and_seed.sh` calls `python -m meal_planner_app.seed_db` only via `seed_if_empty` when not migrating. Change `if __name__` to `seed_if_empty` when an env `SEED_IF_EMPTY=1` is set, **or** add `seed_if_empty` as the script invoked:

```bash
python -c "from meal_planner_app.seed_db import seed_if_empty; seed_if_empty()"
```

Keep `python -m meal_planner_app.seed_db` as full reset seed for explicit use.

- [ ] **Step 3:** Dockerfile: `ENV MEAL_PLANNER_DB=/app/data/meal_planner.db`, `mkdir /app/data && chown appuser`. gitignore `*.db` and `data/*.db`. dockerignore `*.db`.
- [ ] **Step 4:** Commit `feat: persist SQLite file under data/; seed only when empty`

---

### Task 6: Docs + verification

**Files:** `.ai/next_step.md`, `.ai/progress.md`, `.ai/stack.md`, `.ai/migration_plan.md` as needed

- [ ] **Step 1:** Mark persistent DB **Done** (SQLite + DAO). Next is not storage.
- [ ] **Step 2:** Docker gate:

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/ -q --tb=short
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev python -m black --check .
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pylint --rcfile=.pylintrc meal_planner_app
```

- [ ] **Step 3:** Commit docs with the code.

---

## Spec coverage

| Requirement | Task |
|---|---|
| Nested DAO protocols, SQL only in sqlite.py | 1 |
| Master ingredients table first | 1 |
| Recipe lines FK to ingredients, RESTRICT delete | 2 |
| Meal plans + shopping snapshots | 3 |
| crud facade, get-or-create, search stays Python | 4 |
| Seed only if empty, file path, gitignore | 5 |
| Docs | 6 |
| Auth / SQLAlchemy / Alembic | Out of scope |
