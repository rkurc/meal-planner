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

**Verification (Docker `meal-planner:dev`, PYTHONPATH=/app for pylint):**
- pytest: **96 passed**
- black `--check`: clean
- pylint: **10.00/10**

## Next (not this branch)

- Push / PR / babysit if requested
- Master-ingredient UI CRUD (table exists)
- Auth, OpenAPI, discovery

## Out of scope here

SQLAlchemy, Alembic, multi-worker gunicorn, Postgres adapter (protocols are ready).
