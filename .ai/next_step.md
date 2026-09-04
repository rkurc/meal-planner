# .ai/next_step.md — Handoff

**Branch:** `feat/persistent-sqlite-dao`
**Last updated:** 2026-09-04

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Persistent storage: SQLite file behind nested DAOs. Spec: `docs/superpowers/specs/2026-09-04-persistent-sqlite-dao-design.md`. Plan: `docs/superpowers/plans/2026-09-04-persistent-sqlite-dao.md`.

**Layers:** Flask → `crud.py` (get-or-create, search, shopping math) → `MealPlannerDao` (`ingredients` / `recipes` / `meal_plans` / `shopping_lists`) → `SqliteDao` (only `sqlite3`).

**Schema:** `ingredients` master first (unique name, default_unit, location). Recipe lines FK `ingredient_id` ON DELETE RESTRICT. Shopping list items are snapshots.

**File:** `MEAL_PLANNER_DB` or `data/meal_planner.db`. Tests: `:memory:` via `tests/conftest.py`. `start_and_seed.sh` uses `seed_if_empty()`.

**CI babysit (PR #40):** native `backend` pytest failed on
`TestMealPlanApi.test_create_update_meal_plan_with_recipe_counts_api`
(`AssertionError: 0.25 != 1.5`). Cause: `SELECT ... FROM meal_plan_recipes WHERE meal_plan_id = ?`
used the composite PK index, so order followed `recipe_id` UUID strings, not insert order.
Fix: `ORDER BY rowid` in `_SqliteMealPlanDao._from_row`; GET assertion is now a count map;
DAO regression test forces reverse UUID order.

**Verification (Docker `meal-planner:dev`, PYTHONPATH=/app for pylint):**
- pytest: **97 passed** (`python -m pytest meal_planner_app/tests/ -q --tb=short`)
- black `--check`: clean (`python -m black --check` on changed files)
- pylint: **10.00/10** (`python -m pylint meal_planner_app`)

## Next (not this branch)

- Re-check PR #40 CI after the order-fix push
- Master-ingredient UI CRUD (table exists)
- Auth, OpenAPI, discovery

## Out of scope here

SQLAlchemy, Alembic, multi-worker gunicorn, Postgres adapter (protocols are ready).
