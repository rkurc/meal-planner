# .ai/next_step.md — Handoff

**Branch:** `main`
**Last updated:** 2026-09-10
**HEAD:** `9801cd9` (PR #56)

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

PR **#56** (`refactor/abc-follow-up`) merged to `main`. A/B/C leftover items from PR #55 are done:

1. Removed dead `recipe_ids` read fallback in `MealPlanForm.jsx`
2. All React components use `api.js` (no raw `fetch(`)
3. `api_get_meal_plans` shares one `list_recipes()` map
4. `test_crud_exports` locks every `crud.__all__` name
5. README / legacy schema / package README point at `tools/migrate_legacy.py` and `pdf.py`
6. E2E shopping-list comment matches `dao.reset()`; PUT uses `recipes`

CI on PR #56 and on `main` @ `9801cd9`: backend, frontend, docker, integration — all success.

Optional remaining: SQL `GROUP BY` usage counts; dedicated `SEED_DB` env.

## Next

Unrelated product work on a **new** branch: auth; OpenAPI; calendar; prep-time.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
