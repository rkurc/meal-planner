# .ai/next_step.md — Handoff

**Branch:** `refactor/c4-drop-legacy-payloads` (from `refactor/abc`)
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Plan C Task 4 (C4): drop meal-plan JSON `recipe_ids` and Jinja HTML 302 aliases.

| Task | SHA | Status |
|---|---|---|
| A1–A5 | on `refactor/abc` | done |
| B1–B7 | on `refactor/abc` | done |
| C3 migrate_legacy | `eef6264` | done |
| C4 drop recipe_ids + Jinja 302s | this commit | done |
| C1 create_app() | next | pending |
| C2 split crud.py | after C1 | pending |

### C4 done

- `_meal_plan_to_dict` emits `recipes: [{id, name, count}]` only — no `recipe_ids`.
- POST/PUT `/api/meal-plans` still accept `data.get("recipes") or data.get("recipe_ids")` so old clients do not wipe plans.
- Deleted Jinja HTML GET aliases (`/recipes`, `/meal-plans`, shopping-list HTML, `_redirect_ui`).
- Kept `GET /` → `/ui/`, trailing-slash 308 normalizer, and PDF routes.
- `create_app()` is not present on this tree (still module-level `app = Flask(__name__)`).

Verified:

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/test_api.py meal_planner_app/tests/test_pdf.py -q --tb=short
# 56 passed (test_app_factory.py does not exist)

docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pylint meal_planner_app/main.py
# 10.00/10
```

MealPlanForm still *reads* `recipe_ids` as a fallback; it does not send it.
E2E `shopping-lists.spec.js` still PUTs `recipe_ids` (write path remains accepted).

## Next

C1 `create_app()` with opt-in seed route, then C2 split `crud.py`.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
`create_app()` was not added in C4.
