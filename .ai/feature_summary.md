# Feature Summary

This document outlines the major features of the Meal Planning Tool. **Status is reconciled against the current tree as of 2026-09-02.** See `.ai/progress.md` for the capability matrix.

## High-Level Summary

*   **Automatic Recipe Discovery:** *(NOT IMPLEMENTED)* Planned: search-based discovery + direct URL extraction. No scraping/NLP/UI exists.
*   **Ingredient Management:** *(PARTIAL)* Flexible units and locations on ingredients **embedded in recipes**. Read-only aggregated list at `/ui/ingredients`. Suggestion APIs exist. **No standalone master CRUD or persistence.**
*   **Recipe Management:** CRUD with name, description, instructions, source URL, and structured ingredients. **Implemented** in API + React. Prep time / actual time / shelf life are **not** in the model (see requirements). Local search/filter is **implemented** (`GET /api/recipes?q=&ingredient=` + `RecipeList`).
*   **Meal Plan Management:** CRUD plus recipe **counts/multipliers**. **Implemented** in API + React.
*   **Shopping List Generation:** Generate from a meal plan (qty × count, location grouping), persist, edit, create standalone lists, delete, PDF. **Implemented** in API + React.
*   **Modern UI:** React SPA (Vite / Tailwind 4) at `/ui/` is the **only HTML UI**. `GET /` 302 → `/ui/`. Nav: Recipes, Ingredients, Meal Plans, Shopping Lists. Jinja templates are gone.
*   **API:** REST for recipes, meal-plans, shopping-lists, plus ingredient/unit/location suggestion and summary endpoints. **No auth.**

## Detailed Feature Descriptions

### Automatic Recipe Discovery *(NOT IMPLEMENTED)*

**Status (2026-09-02):** Still zero implementation. No web search, scraping, or URL extraction in Python or JS.

Intended modes (unchanged):

1.  **Search-Based Discovery:** Query by ingredients or dish type; present candidates to import.
2.  **URL-Based Extraction:** User pastes a URL; extract fields and pre-fill the Add Recipe form.

### Ingredient Management *(PARTIAL — embedded + read-only aggregation)*

**Status:** Ingredients are denormalized on `Recipe`. There is no `produkty`-style master table in the running app (legacy CSVs *do* have one; migration copies name/unit/location onto each recipe line).

What exists:

*   Flexible **quantity + unit** (FR-1.3.4) used in recipes, shopping consolidation, and forms.
*   Optional **location / location_id** (shopping aisle) on ingredients and shopping items.
*   `GET /api/ingredients` — unique names (autocomplete).
*   `GET /api/ingredients/summary` — `{name, usage_count, unit, location}` for the list page.
*   `GET /api/ingredients/info?name=` — recipes using that exact name (API only; React detail route removed).
*   `GET /api/locations`, `GET /api/units`.
*   React `/ui/ingredients`: one-line list; "Add new ingredient" navigates to **new recipe**, not a master create form.
*   Default unit auto-filled when picking a known name (if the unit field is empty).

What does **not** exist: create/edit/delete of a unique master ingredient, or syncing a name change across recipes.

### Recipe Management

CRUD for a collection of recipes. Stored fields:

*   Name, description, instructions, source URL.
*   Ingredients: name, quantity, unit, location, location_id.

**Not stored (despite older docs / FR-1.2.1):** declared preparation time, actual preparation time, shelf life.

**Implementation status:** Full CRUD in React (`RecipeList` / `Detail` / `Form`) and `/api/recipes`. React forms use datalists for names/units/locations. Recipe search/filter is on the React list and the JSON API. Jinja recipe pages are gone.

### Meal Plan Management

Named plans with a list of `{recipe_id, count}` (fractional counts allowed; shopping quantities multiply). Legacy `recipe_ids` still accepted and returned.

**Implementation status:** API + React (`MealPlanList` / `Detail` / `Form` with dropdown + count). No calendar / date-range model. Jinja meal-plan pages are gone.

### Shopping List Generation

From a meal plan: consolidate identical name+unit+location; leave incompatible units separate. Persist as `ShoppingList` with editable items (`purchased`, location). Standalone empty lists via `POST /api/shopping-lists` with `{name}`. Delete via API + React. PDF:

*   Persisted list: `GET /shopping-lists/<uuid>/pdf` (React "Download PDF"; skips purchased).
*   Meal-plan generated: `GET /meal-plans/<uuid>/shopping-list/pdf` (kept; no HTML shopping table).

### Modern User Interface (React)

Vite + React 18 + react-router-dom v7 + Tailwind 4, basename `/ui`. Axios used in meal-plan components; `fetch` elsewhere.

**Coverage:** Recipes (CRUD + search), Ingredients (list only), Meal Plans (CRUD + counts + embedded shopping), Shopping Lists (chooser / create / edit / delete / PDF).

Flask does not render HTML templates. Old bookmarks (`/`, `/recipes`, `/meal-plans`, …) 302 into `/ui/…`.

### APIs

Unauthenticated JSON API. See `meal_planner_app/main.py`. Notable paths:

- `/api/recipes` CRUD + list filters `q`, `ingredient`
- `/api/meal-plans` CRUD + `.../recipes` + `.../shopping-list` (grouped generate)
- `/api/shopping-lists` CRUD (create from meal plan **or** standalone)
- `/api/ingredients`, `/api/ingredients/summary`, `/api/ingredients/info`
- `/api/locations`, `/api/units`
- PDF routes are **not** under `/api/` (they return `application/pdf`)
- `/api/test/seed-db` only when `TESTING` / debug

### Future Goals / Desired Features

*   **Automatic Recipe Discovery** and **master ingredients**.
*   **Auth, OpenAPI, persistent DB.**
*   **PDF** — shopping-list PDF is done from React; meal-plan PDF as a document is not a separate feature.
*   Local recipe search in React is **done** (no longer a future item).
