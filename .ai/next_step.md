# .ai/next_step.md — Handoff

**Branch:** `refactor/b2-catalog-hook` (from `refactor/abc`)
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Plan B Task 2 (`useCatalogLookups` + shared ingredient line fields) on `refactor/b2-catalog-hook`.

- Added `frontend/src/defaultUnit.js` (`applyDefaultUnit`) with TDD in `frontend/src/defaultUnit.test.js` (fail first: module missing, then pass).
- Added `frontend/src/hooks/useCatalogLookups.js`: on mount `api.get` `/api/ingredients/summary`, `/api/locations`, `/api/units`. Returns `{ knownIngredients, knownLocations, knownUnits, ingredientDefaultUnits }`. Lookup failures are non-fatal (empty arrays / empty map).
- Added `frontend/src/components/IngredientLineFields.jsx` (name/qty/unit/location + remove). Datalists stay in the parent (`known-ingredients` / `known-units` / `known-locations`).
- Wired `RecipeForm.jsx` and `ShoppingListView.jsx`: deleted the four duplicated catalog fetch blocks; change handlers use `applyDefaultUnit`. Shopping list keeps grouping, edit/view modes, source-recipe tooltips, no checkboxes, `purchased: false` on add.
- MealPlan* files unchanged.
- Verified in `meal-planner:dev` (anonymous volume for image `node_modules`):
  `npm run test:unit` — 34 pass / 0 fail (includes `applyDefaultUnit`)
  `npm run lint` — pass
  `npm run format-check` — pass after prettier wrap of hook destructures in RecipeForm/ShoppingListView

## Next

Plan B remaining: B4 meal-plan recipe names, B3 collapse ingredient GETs (hook currently uses `/api/ingredients/summary` until then), B7 E2E hygiene.

Then Plan C.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
