# .ai/next_step.md — Handoff

**Branch:** `refactor/b4-meal-plan-names`
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Plan B Task 4: meal-plan JSON includes recipe names.

- `_meal_plan_to_dict` now emits `{id, name, count}` per recipe (names from `crud.list_recipes()` map; missing recipe → `name: ""`).
- Still emits `recipe_ids` (Plan C4 drops it).
- `MealPlanDetail` renders `mealPlan.recipes` directly (no extra `GET /api/recipes` join) and links names to `/recipes/:id`.
- Verification:
  - `docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev python -m pytest meal_planner_app/tests/test_api.py -q --tb=short` → **34 passed**
  - `docker run --rm -v "$(pwd)/frontend:/app/frontend" -v /app/frontend/node_modules -w /app/frontend meal-planner:dev npm run lint` → pass
  - `docker run --rm -v "$(pwd)/frontend:/app/frontend" -v /app/frontend/node_modules -w /app/frontend meal-planner:dev npm run format-check` → pass

| Task | SHA | Status |
|---|---|---|
| A1–A5 | on `refactor/abc` | done |
| B1 api.js / drop axios | `da7fa1a` | merged |
| B5 JSON /api errors | `2118281` | merged |
| B6 batch find_all | `82baede` | merged |
| B4 meal-plan recipe names | this branch | done (unmerged) |
| B2 catalog hook + line fields | next |
| B3 collapse ingredient GETs | after B2 |
| B7 E2E hygiene | after B2/B4 |

## Next

Merge B4 onto `refactor/abc`. Finish Plan B (B2, B3, B7), then Plan C.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
