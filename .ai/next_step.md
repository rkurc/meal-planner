# .ai/next_step.md — Handoff

**Branch:** `refactor/a2-meal-plan-put`
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

A2 (Plan A Task 2): meal-plan PUT/POST correctness.

- `PUT /api/meal-plans/<id>` with `{name}` only no longer wipes recipes; `recipes=` is passed only when `"recipes"` or `"recipe_ids"` is in the body.
- `POST /api/meal-plans/<id>/recipes` returns 404 for unknown `recipe_id` (`add_recipe_to_meal_plan` now returns `None` if recipe missing).
- That POST honors JSON `count` (float, default 1.0; 400 if invalid).

**Verify:**
```
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/test_api.py meal_planner_app/tests/test_crud.py -q --tb=short
# 68 passed in 0.33s
```

TDD: name-only PUT wiped recipes (`[] != [recipe_id]`); missing recipe POST was 200; count stayed 1.0. Then implementation.

## Next

Continue Wave 1 from Plan A (remaining: A1 seed reset, A3 drop checkboxes, A4 MealPlanForm errors, A5 Vite PDF proxy). Optional: B6 batch find_all, C3 move migrate_legacy.

Then Plan B, then Plan C (C3 may already be done).

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; second DAO backend; persisting purchased checkboxes.
