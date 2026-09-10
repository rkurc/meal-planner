# .ai/next_step.md — Handoff

**Branch:** `refactor/abc-follow-up`
**Last updated:** 2026-09-10
**Base:** `origin/main` after PR #55 (`cd1a9fe`)

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

PR **#55** (`refactor/abc`) merged to `main`. Follow-up from the A/B/C review is on this branch:

1. Removed dead `recipe_ids` read fallback in `MealPlanForm.jsx`
2. All React components use `api.js` (no raw `fetch(`)
3. `api_get_meal_plans` shares one `list_recipes()` map
4. `test_crud_exports` locks every `crud.__all__` name
5. README / legacy schema / package README point at `tools/migrate_legacy.py` and `pdf.py`
6. E2E shopping-list comment matches `dao.reset()`; PUT uses `recipes`

Optional remaining: SQL `GROUP BY` usage counts; dedicated `SEED_DB` env.

## Next

Open/merge the follow-up PR. Unrelated product work: auth; OpenAPI; calendar; prep-time.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
