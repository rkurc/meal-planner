# Implementation Summary

Overview of what is implemented versus remaining work. **Reconciled 2026-09-02 against `feat/decommission-jinja-ui`.** Canonical matrix: `.ai/progress.md`.

The 2026-08-25 snapshot (hybrid Jinja + React, 78 pytest, 9 E2E, search Jinja-only) is obsolete. Jinja HTML is **gone**.

## 1. Current Implemented Features

Headless-ish Flask API (JSON + PDF + SPA static + legacy GET **redirects**), React SPA at `/ui/` as the **only HTML UI**. Storage is **in-memory** (lost on process restart; seed / migrate on start).

### Backend & API

*   **Recipe API (`/api/recipes`):** GET list (optional `q` + `ingredient` filters via `crud.search_recipes`), POST, GET/PUT/DELETE by id. Ingredients include `location` / `location_id`. Empty search params still list all.
*   **Meal Plan API (`/api/meal-plans`):** CRUD; `recipes: [{id, count}]` plus legacy `recipe_ids`; add/remove recipe; `GET .../shopping-list` returns **grouped-by-location** dict (qty multiplied by count).
*   **Shopping List API (`/api/shopping-lists`):** POST from `meal_plan_id` **or** standalone `{name}`; GET list/id; PUT items; DELETE.
*   **Suggestion / aggregation APIs:**
    *   `GET /api/ingredients` — unique names
    *   `GET /api/ingredients/summary` — name, usage_count, unit, location
    *   `GET /api/ingredients/info?name=` — usage + slim recipes
    *   `GET /api/locations`, `GET /api/units`
*   **PDF:** `GET /shopping-lists/<id>/pdf` (persisted, exclude purchased); `GET /meal-plans/<id>/shopping-list/pdf` (generated; missing list → 404). Helpers in `crud.shopping_list_to_pdf_data` + `services.generate_shopping_list_pdf`.
*   **Models (dataclasses / classes, in-memory lists):** `Recipe`, `Ingredient`, `MealPlan`, `ShoppingList` / `ShoppingListItem`.
*   **Search:** `crud.search_recipes(query, filter_ingredient)` exposed as `GET /api/recipes?q=&ingredient=`.
*   **Legacy ingest:** `migrate_legacy.py` (relational CSV preferred over heuristic `.odb`). `migrate_legacy.parse_ingredients_from_text` remains for CSV ingest (not Jinja).
*   **HTML:** no `render_template`. `GET /` 302 → `/ui/`. Other former Jinja GETs 302 into `/ui/…`. Form POSTs are not served (404/405). `templates/` directory is gone.

### Traditional UI (Jinja2) — decommissioned

Removed: eight HTML templates, form POST handlers, `parse_ingredients_from_textarea`, `nl2br`, Tailwind v3 `static/css` pipeline.

### Modern UI (React @ `/ui/`) — only HTML UI

*   **Recipes:** `RecipeList` (search + ingredient filter), `RecipeDetail`, `RecipeForm` (dynamic ingredient rows, datalists, default unit).
*   **Ingredients:** `IngredientList` only (no subpages). `IngredientDetail.jsx` is **orphaned**.
*   **Meal plans:** list / detail (shows `x {count}`) / form (dropdown + decimal count).
*   **Shopping:** `ShoppingListView` embedded in meal-plan detail **and** standalone `/ui/shopping-lists` (chooser of all lists, create, edit, delete, PDF).
*   **Build:** Vite 7 + Tailwind 4; `npm run format` / `format-check` / `lint`; Playwright.

### Testing & Environment

*   **Backend:** **83** pytest functions (`test_api`, `test_crud`, `test_shopping_list`, `test_shopping_list_api`). Includes search API tests and legacy GET redirect tests. Jinja form HTML tests are gone.
*   **E2E:** **10** Playwright tests in `frontend/e2e/main.spec.js` (recipe CRUD, shopping generate/edit, default unit, **recipe search**).
*   **Docker:** `docker-bake.hcl` targets `dev` / `prod` / `ci`. Task 5 observed `docker buildx bake prod` DONE. Full Task 7 suite is a separate verification pass.
*   **Seed:** `seed_db.py` + `start_and_seed.sh` + `/api/test/seed-db` (guarded).
*   **Quality:** pre-commit black + pylint; prettier + eslint.

## 2. Remaining Work

### Not started (not Jinja leftovers)

*   **Automatic Recipe Discovery** (FR-1.1).
*   **Master ingredient CRUD** (FR-1.3.1–1.3.3) and any sync into recipes.
*   **API authentication.**
*   **OpenAPI/Swagger.**
*   **Persistent database.**
*   **Recipe prep / actual time / shelf life** (specified in FR-1.2.1, never modeled).
*   **Meal calendar / date range.**
*   **Frontend unit tests** (Jest/RTL).

### Partial

*   **Ingredient views:** list + APIs; no detail route; no master writes.
*   **PDF:** shopping list yes; not a meal-plan document export.
*   **i18n:** PDF sanitization + optional DejaVu; UI not localized.
*   **Prod image:** works but includes Node/Vite for the shared start script.
*   **E2E:** recipes (including search) + embedded shopping happy path; not ingredients, standalone lists, delete, or PDF.
*   **`list_unique_locations`:** can return unresolved IDs mixed with names.

### Cleanup opportunities

*   Remove or re-route `IngredientDetail.jsx`.
*   Combine suggestion fetches (`Promise.all` / shared hook).

### Testing status (inventory, not a fresh Task 7 run)

- Backend: 83 tests in tree.
- E2E: 10 tests in `main.spec.js`.
- Missing tests called out in `.ai/progress.md` and `.ai/test_plan.md`.
