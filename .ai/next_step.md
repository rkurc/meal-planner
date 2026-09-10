# .ai/next_step.md — Handoff

**Branch:** `refactor/b5-json-errors` (from `refactor/abc`)
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Plan B Task 5: JSON error handler for `/api/*`.

- Added `TestApi.test_api_400_returns_json_error` (empty `POST /api/recipes` must be 400 JSON with `error`).
- TDD: first run failed (`text/html; charset=utf-8` != `application/json`).
- Registered `@app.errorhandler(HTTPException)` in `meal_planner_app/main.py`: `/api/` paths return `jsonify({"error": ...})`; PDF and `/ui` still return the exception (HTML).
- Verification (Docker `meal-planner:dev`):
  - `python -m pytest meal_planner_app/tests/test_api.py meal_planner_app/tests/test_ingredient_api.py -q --tb=short` → **48 passed**
  - `python -m pylint --rcfile=.pylintrc meal_planner_app/main.py` → **10.00/10**

## Next

Remaining Plan B (`docs/superpowers/plans/2026-09-10-refactor-b-simplification.md`): `api.js`, catalog hook, collapse ingredient GETs, meal-plan names, N+1 `find_all`, E2E hygiene.

Then Plan C. C3 (move `migrate_legacy`) can still run in parallel with B. C factory work depends on B5 so the handler is registered inside the factory.

## Out of scope
Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
