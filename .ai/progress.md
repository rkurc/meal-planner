# Progress Tracker

**As of:** 2026-09-06
**Code snapshot:** branch `chore/i18n-ops-cleanup` on top of `main` @ `76b0b64` (i18n chrome #47).
**Last prior docs reconciliation:** 2026-09-02 (Jinja decommission). This pass records **master-ingredient CRUD, shopping grouping + g↔kg, i18n leftover chrome, lean prod, and extra tests**.

Canonical status lives here. Other `.ai/*.md` files and the root README should match this snapshot.

**HTML UI:** React SPA at `/ui/` only. `GET /` 302 → `/ui/`. Other former Jinja HTML GETs 302 into `/ui/…`. `meal_planner_app/templates/` is gone; form POST handlers are gone; leftover Tailwind v3 CSS pipeline is gone.

## Legend

| Status | Meaning |
|---|---|
| **Done** | Present in code and usable |
| **Partial** | Exists but incomplete vs the original requirement |
| **Missing** | Not implemented |
| **N/A** | Not applicable in that layer |
| **Decommissioned** | Removed; React + API is the replacement |

## Feature matrix (docs vs code)

### Recipes

| Capability | Backend | React `/ui/` | Legacy Jinja | Tests | Status |
|---|---|---|---|---|---|
| CRUD (name, description, instructions, source URL, ingredients) | Done | Done | Decommissioned | pytest + 5 E2E | **Done** |
| Structured ingredient rows (name / qty / unit / location) | Done | Done (dynamic rows + datalists) | Decommissioned | pytest + E2E | **Done** |
| Autocomplete: ingredient names, units, locations | Done (`/api/ingredients`, `/api/units`, `/api/locations`) | Done | Decommissioned | pytest for list endpoints | **Done** |
| Default unit on name select (if unit empty) | Done via `/api/ingredients/summary` | Done (RecipeForm + ShoppingListView) | Decommissioned | 2 E2E | **Done** |
| Recipe search (name / description / ingredients + ingredient filter) | Done (`GET /api/recipes?q=&ingredient=` via `crud.search_recipes`) | Done (`RecipeList`) | Decommissioned | 19 unit + 4 API + 1 E2E | **Done** |
| Declared prep time, actual prep time, shelf life (FR-1.2.1) | Missing | Missing | Decommissioned | Missing | **Missing** (never in the model) |
| Automatic recipe discovery / URL extract (FR-1.1) | Missing | Missing | Decommissioned | Future TCs | **Missing** |

### Ingredients (standalone)

Master ingredient table + `/ui/ingredients` CRUD landed in #42. Recipe rows still store name/qty/unit/location; the catalog is the source for defaults and usage.

| Capability | Backend | React `/ui/` | Legacy Jinja | Tests | Status |
|---|---|---|---|---|---|
| Unique names for autocomplete | Done `GET /api/ingredients` | Used by forms | Decommissioned | pytest | **Done** |
| Summary list (name, usage_count, unit/location) | Done `GET /api/ingredients/summary` | Done `IngredientList` (links to detail) | Decommissioned | pytest + E2E | **Done** |
| Detail: recipes using this ingredient | Done `GET /api/ingredients/<id>` (+ `/info?name=`) | Done `IngredientDetail` | Decommissioned | pytest + E2E | **Done** |
| Create / edit / delete a master ingredient (FR-1.3.1–1.3.3) | Done | Done (`/ingredients/new`, `/:id/edit`; 409 if still used) | Decommissioned | pytest + E2E | **Done** |
| Flexible units on embedded ingredients (FR-1.3.4) | Done | Done | Decommissioned | pytest + E2E | **Done** |
| Location (aisle) on ingredient | Done (`location` + `location_id`) | Done on catalog, recipe form, shopping edit | Decommissioned | pytest locations | **Done** |

### Meal plans

| Capability | Backend | React `/ui/` | Legacy Jinja | Tests | Status |
|---|---|---|---|---|---|
| CRUD name + description | Done | Done | Decommissioned | pytest | **Done** |
| Add/remove recipes | Done | Done | Decommissioned | pytest | **Done** |
| Recipe **counts / multipliers** (fractions OK) | Done (`recipes: [{id, count}]` + legacy `recipe_ids`) | Done (dropdown + number) | Decommissioned | pytest | **Done** |
| Shopping list from plan (qty × count, location groups) | Done | Done (persist + edit) | Decommissioned | pytest + 2 E2E | **Done** |
| Date range / calendar (FR-1.4.1 wording) | Missing | Missing | Decommissioned | Missing | **Missing** |

### Shopping lists

| Capability | Backend | React `/ui/` | Legacy Jinja | Tests | Status |
|---|---|---|---|---|---|
| Generate + consolidate compatible units | Done (same unit + g↔kg / ml↔l) | Done | Decommissioned | pytest | **Done** |
| Persist + edit items (add/remove/qty/unit/location/purchased) | Done `/api/shopping-lists` | Done | Decommissioned | pytest + 1 E2E | **Done** |
| Standalone list (`POST {name}` → empty) | Done | Done (chooser + create) | Decommissioned | pytest + E2E | **Done** |
| Delete list | Done `DELETE` | Done (picker + detail) | Decommissioned | pytest + E2E | **Done** |
| PDF of **persisted** list (exclude purchased) | Done `GET /shopping-lists/<id>/pdf` | Done (Download PDF) | Decommissioned | pytest + E2E | **Done** |
| PDF of **meal-plan generated** list | Done `GET /meal-plans/<id>/shopping-list/pdf` | Missing (React uses persisted route) | Decommissioned (HTML); PDF route kept | pytest PDF | **Done** (API) |
| Location grouping in PDF | Done | N/A (server PDF) | Decommissioned | pytest `location_id` | **Done** |
| Location grouping in HTML | N/A | Headings by location (`ShoppingListView`) | Decommissioned | node:test grouping + E2E | **Done** |

### Platform / quality

| Capability | Status | Notes |
|---|---|---|
| In-memory store | **Replaced** | SQLite file via DAO; tests still use `:memory:` |
| Legacy CSV / `.odb` migration | **Done** | Relational CSV preferred (`przepisy` + `skladniki` + `produkty`) |
| Docker bake (`dev` / `prod` / `ci`) | **Done** | Node 20 + Python 3.9; `ci`/`dev` copy Node from `node:*-bullseye` (no nodesource/gnupg apt) |
| pre-commit (black, pylint) + prettier + eslint | **Done** | Docker-first in AGENTS.md |
| Backend tests | **Done** | pytest (DAO + CRUD/API + units + PDF) |
| E2E Playwright | **Done** | **15** tests: recipes, search, meal-plan shopping, ingredients CRUD, standalone list + PDF + delete, PL smoke |
| API auth (JWT / login) | **Missing** | All routes open |
| OpenAPI / Swagger | **Missing** | |
| Persistent DB (SQLite/Postgres) | **Done** (SQLite) | `data/meal_planner.db`; nested DAOs; Postgres would implement the same protocols |
| Decommission Jinja (migration Phase 3) | **Done** | Templates, form POSTs, Tailwind v3 CSS gone; GET redirects to `/ui/` |
| i18n (Polish in UI + lossless PDF) | **Done** (chrome) | react-i18next en/pl including IngredientForm/Detail + recipe placeholder hint; content not MT; PDF DejaVu + NFC + `?lang=` |
| Lean production image (no Node/Vite runtime) | **Done** | `prod` is Python + gunicorn + prebuilt `/ui/`; no Node, no apt |
| Frontend unit tests | **Done** | `node --test src` (placeholder instructions, leftover chrome scan, shopping grouping); not Jest/RTL |

## What landed on `feat/decommission-jinja-ui` (2026-09-02)

1. **Search API** (`5b2df09`): `GET /api/recipes?q=&ingredient=` filters via `crud.search_recipes`. Empty both params still lists all.
2. **React recipe search** (`a526cd8`): `RecipeList` search + ingredient filter; Playwright search test.
3. **Jinja HTML gone** (`789212c`): legacy GET paths 302 to `/ui/…`; templates and form POST handlers removed; PDF 404 on missing generated list.
4. **Tailwind v3 CSS pipeline gone** (`e273724`): no `npx tailwindcss@3` in Dockerfile; root `package.json` is a `build:react` wrapper only; `static/css/` deleted.

## Known leftover / dead code

- `GET /api/ingredients/info` — still used as a name lookup; UI detail is `/api/ingredients/<id>`.
- `list_unique_locations()` still falls back to raw `location_id`, so datalists can mix `"Dairy"` and `"4"`.
- RecipeForm / ShoppingListView still use several independent `fetch` chains (optional `Promise.all` cleanup).

## Recommended next work (priority)

1. API auth + OpenAPI.
2. Automatic recipe discovery (still the largest unimplemented original feature).
3. Recipe metadata (prep / actual time / shelf life) if those FRs are still desired.
4. Meal-plan calendar / date range (FR-1.4.1).
5. Meal-plan-as-PDF document (shopping PDF is done).
