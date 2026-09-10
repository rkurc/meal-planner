# .ai/next_step.md — Handoff

**Branch:** `refactor/abc`
**Last updated:** 2026-09-10
**HEAD:** `6c6fb85` (+ follow-up notes commit)

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

A/B/C refactor is on `refactor/abc`. A3 = drop purchased checkboxes. Review fixes: `seedDb` asserts HTTP OK; `start_and_seed.sh` exports `TESTING=true`. Playwright **20 passed**.

## Follow-up (after `refactor/abc` merges)

Do this on a **new branch from `main`** (e.g. `refactor/abc-follow-up`). Keep each item a small commit.

1. **Dead `recipe_ids` read fallback** — `frontend/src/components/MealPlanForm.jsx` still maps `data.recipe_ids` if `data.recipes` is missing. API no longer emits `recipe_ids`. Delete the fallback; keep write-side acceptance on the backend for one more release.
2. **Adopt `api.js` for remaining CRUD** — `RecipeForm.jsx`, `RecipeDetail.jsx`, `IngredientForm.jsx`, `IngredientDetail.jsx`, `IngredientList.jsx`, `ShoppingListView.jsx` still use raw `fetch`. Switch to `api.get/post/put/del` so B5 JSON `{error}` bodies surface. Do not add React Query.
3. **Meal-plan list N+1 names** — `_meal_plan_to_dict` (`meal_planner_app/main.py`) calls `crud.list_recipes()` per plan. Cache one map in `api_get_meal_plans`.
4. **Lock `crud` re-exports** — expand `meal_planner_app/tests/test_crud_exports.py` to the full `__all__` list in `crud.py` (or import `__all__` and assert each name).
5. **Docs for migrate path** — README and `docs/legacy_przepisy_schema.md` still say `python -m meal_planner_app.migrate_legacy`. Point at `python tools/migrate_legacy.py`. Update `meal_planner_app/README.md` if it still lists `services.py`.
6. **Stale E2E comment** — `frontend/e2e/shopping-lists.spec.js` still claims seed-db keeps the meal plan and stale recipe IDs (the A1 bug). Rewrite the comment to match `dao.reset()`.

Optional / later (not blocking):

- SQL `GROUP BY` for `list_ingredients_summary` usage counts
- Dedicated `SEED_DB` env instead of overloading Flask `TESTING`

Out of scope: auth; OpenAPI; calendar; React Query; SQLAlchemy; persisting purchased checkboxes.

## Next

Open PR for `refactor/abc`, wait for CI, merge, then start follow-up item 1 on a new branch.
