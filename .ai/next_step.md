# .ai/next_step.md — Handoff

**Branch:** `refactor/a1-seed`
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

A1 seed reset: `seed_database()` now calls `get_dao().reset()` (wipes recipes, meal plans, shopping lists) then inserts `RECIPES_TO_SEED` and recreates Weekly Meal Plan. `seed_if_empty` / `seed_meal_plans` unchanged.

**Evidence:**
- TDD red: `docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev python -m pytest meal_planner_app/tests/test_seed.py -q --tb=short` → FAIL `assert 0 == 2` on Weekly Meal Plan recipes after second seed.
- Green: same image `python -m pytest meal_planner_app/tests/test_seed.py meal_planner_app/tests/test_crud.py -q --tb=short` → **38 passed**, including `test_seed_if_empty_is_idempotent`.

## Next

Wave 1 remaining (parallel, isolated worktrees): A2 meal-plan PUT, A3 drop checkboxes, A4 MealPlanForm errors, A5 Vite PDF proxy. Optional: B6 batch find_all, C3 move migrate_legacy.

Then Plan B, then Plan C.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; second DAO backend; persisting purchased checkboxes.
