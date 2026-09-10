# .ai/next_step.md — Handoff

**Branch:** `refactor/c2-split-crud`
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Plan C Task 2: split `crud.py` into `domain/*` with a compatibility re-export; rename `services.py` → `pdf.py`.

- Added `meal_planner_app/tests/test_crud_exports.py` first (passed on unsplit `crud.py`).
- Moved functions into:
  - `meal_planner_app/domain/_dao.py` (`set_dao` / `get_dao`)
  - `meal_planner_app/domain/recipes.py`
  - `meal_planner_app/domain/meal_plans.py`
  - `meal_planner_app/domain/shopping.py`
  - `meal_planner_app/domain/ingredients.py`
- `meal_planner_app/crud.py` is now an explicit re-export (`__all__` listed).
- Renamed `services.py` → `pdf.py`; updated `main.py` and `tests/test_pdf.py`. No `services.py` shim (Python grep clean).

**Verify:**
```
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  sh -c 'python -m pytest meal_planner_app/tests/ -q --tb=short && python -m pylint --rcfile=.pylintrc meal_planner_app'
```
225 passed; pylint 10.00/10.

## Next

Finishing-a-development-branch (PR / merge options). Plan C is complete.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
