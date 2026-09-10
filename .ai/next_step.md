# .ai/next_step.md — Handoff

**Branch:** `refactor/b6-batch-find-all` (from `refactor/abc`)
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Plan B Task 6: batch-load child rows in DAO `find_all` (N+1 removal). Behavior-preserving.

- Regression locks first (passed on old N+1 `find_all`):
  - `test_find_all_does_not_cross_ingredient_lines`
  - `test_find_all_does_not_cross_recipe_entries`
  - `test_find_all_does_not_cross_shopping_list_items`
- Then `find_all` for recipes / meal plans / shopping lists: parent SELECT + one child query, group in Python. `find_by_id` still uses the single-row query.
- Schema and Flask unchanged.

**Verify:**
```
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/test_dao.py meal_planner_app/tests/test_crud.py meal_planner_app/tests/test_api.py -q --tb=short
```
86 passed. `python -m pylint meal_planner_app/dao/sqlite.py` → 10.00/10.

## Next

Plan B remaining: B1 `api.js`, B2 catalog hook, B3 collapse ingredient GETs, B4 meal-plan names, B5 JSON errors, B7 E2E hygiene.

Then Plan C. C3 (move `migrate_legacy`) can still run in parallel with B.

## Out of scope
Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
