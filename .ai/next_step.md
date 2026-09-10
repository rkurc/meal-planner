# .ai/next_step.md — Handoff

**Branch:** `refactor/b3-ingredient-list-objects` (from `refactor/abc`)
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Wave 1 (Plan A) merged. Plan B in progress:

| Task | SHA | Status |
|---|---|---|
| A1–A5 | on `refactor/abc` | done |
| B1 api.js / drop axios | `da7fa1a` | merged |
| B5 JSON /api errors | `2118281` | merged |
| B6 batch find_all | `82baede` | merged |
| B2 catalog hook + line fields | `688e968` | merged |
| B4 meal-plan recipe names | `c818bad` | merged |
| B3 collapse ingredient GETs | this commit | done |
| B7 E2E hygiene | next | pending |

### B3 done

`GET /api/ingredients` now returns `[{id, name, usage_count, unit, location}, ...]`.
`GET /api/ingredients/info` and `GET /api/ingredients/summary` are 404.
POST `/api/ingredients` still creates; `GET /api/ingredients/<uuid>` unchanged.
Frontend hook and IngredientList switched to `GET /api/ingredients`.

Verified:

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/test_ingredient_api.py \
  meal_planner_app/tests/test_shopping_list_api.py meal_planner_app/tests/test_api.py -q --tb=short
# 65 passed

docker run --rm -v "$(pwd)/frontend:/app/frontend" -v /app/frontend/node_modules \
  -w /app/frontend meal-planner:dev sh -c 'npm run test:unit && npm run lint'
# 34 pass, eslint clean
```

`frontend/src` has no remaining `/api/ingredients/info` or `/api/ingredients/summary`.

## Next

B7 E2E hygiene, then Plan C.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
SQL `GROUP BY` usage counts still a Python loop in `list_ingredients_summary`.
