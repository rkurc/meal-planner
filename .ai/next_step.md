# .ai/next_step.md — Handoff

**Branch:** `refactor/b1-api-js` (from `refactor/abc`)
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Plan B Task 1 (`api.js` and drop axios) on `refactor/b1-api-js`.

- Added `frontend/src/api.js` (`api.get/post/put/del` + `ApiError`) and TDD tests in `frontend/src/api.test.js`.
- Replaced axios in `MealPlanList.jsx`, `MealPlanForm.jsx`, `MealPlanDetail.jsx` only.
- MealPlanForm keeps Wave 1 A4 `loadError`/`submitError` split; submitError uses `err.message`; submit payload is `recipes` only (no `recipe_ids`).
- Grep `from "axios"` under `frontend/src` is empty. Removed axios via Docker:
  `docker run --rm -v "$(pwd)/frontend:/app" -w /app node:20-alpine sh -c 'npm uninstall axios'`
- Verified in `meal-planner:dev` (anonymous volume for image `node_modules`):
  `npm run test:unit` — 31 pass / 0 fail
  `npm run lint` — pass
  `npm run format-check` — pass (prettier wrapped one `assert.rejects` line)

RecipeForm / ShoppingListView still use fetch (or other helpers); that is B2.

## Next

Plan B Task 2: `useCatalogLookups` + `IngredientLineFields` + switch RecipeForm/ShoppingListView to `api.js`.

Then B3–B7, then Plan C. C3 (move `migrate_legacy`) can still run in parallel with B.

## Out of scope
Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
