# Progress Tracker

**As of:** 2026-09-02
**Code snapshot:** branch `feat/decommission-jinja-ui` (implementation: `e273724`, `789212c`, `a526cd8`, `5b2df09`; plus this docs commit).
**Last prior docs reconciliation:** 2026-08-25 (hybrid Jinja + React). This pass records **Jinja decommission complete**.

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

Ingredients are still **denormalized inside recipes**. There is **no product master table**.

| Capability | Backend | React `/ui/` | Legacy Jinja | Tests | Status |
|---|---|---|---|---|---|
| Unique names for autocomplete | Done `GET /api/ingredients` | Used by forms | Decommissioned | pytest | **Done** |
| Summary list (name, usage_count, first-seen unit/location) | Done `GET /api/ingredients/summary` | Done `IngredientList` (one line, no subpages) | Decommissioned | Missing | **Partial** (read-only aggregation) |
| Detail: recipes using a name | Done `GET /api/ingredients/info?name=` | Dead code: `IngredientDetail.jsx` exists, **no route** | Decommissioned | Missing | **Partial** (API only) |
| Create / edit / delete a master ingredient (FR-1.3.1–1.3.3) | Missing | "Add new ingredient" → `/recipes/new` | Decommissioned | Future TCs | **Missing** |
| Flexible units on embedded ingredients (FR-1.3.4) | Done | Done | Decommissioned | pytest + E2E | **Done** |
| Location (aisle) on ingredient | Done (`location` + `location_id`) | Done on recipe form + shopping edit | Decommissioned | pytest locations | **Done** |

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
| Generate + consolidate compatible units | Done | Done | Decommissioned | pytest | **Done** |
| Persist + edit items (add/remove/qty/unit/location/purchased) | Done `/api/shopping-lists` | Done | Decommissioned | pytest + 1 E2E | **Done** |
| Standalone list (`POST {name}` → empty) | Done | Done (chooser + create) | Decommissioned | pytest | **Done** |
| Delete list | Done `DELETE` | Done (picker + detail) | Decommissioned | pytest (API); no E2E | **Done** |
| PDF of **persisted** list (exclude purchased) | Done `GET /shopping-lists/<id>/pdf` | Done (Download PDF) | Decommissioned | 3 pytest | **Done** |
| PDF of **meal-plan generated** list | Done `GET /meal-plans/<id>/shopping-list/pdf` | Missing (React uses persisted route) | Decommissioned (HTML); PDF route kept | pytest PDF | **Done** (API) |
| Location grouping in PDF | Done | N/A (server PDF) | Decommissioned | pytest `location_id` | **Done** |
| Location grouping in HTML | N/A | Items show location; not grouped headings | Decommissioned | — | **Partial** |

### Platform / quality

| Capability | Status | Notes |
|---|---|---|
| In-memory store | **Done** (limitation) | Data lost on restart; seed / legacy migrate on start |
| Legacy CSV / `.odb` migration | **Done** | Relational CSV preferred (`przepisy` + `skladniki` + `produkty`) |
| Docker bake (`dev` / `prod` / `ci`) | **Done** | Node 20 + Python 3.9; CI also native jobs. Task 5: `docker buildx bake prod` succeeded |
| pre-commit (black, pylint) + prettier + eslint | **Done** | Docker-first in AGENTS.md |
| Backend tests | **Done** | **83** pytest (inventory in tree; not a fresh Task 7 run) |
| E2E Playwright | **Partial** | **10** tests (includes recipe search); no coverage for ingredients page, standalone lists, delete, PDF |
| API auth (JWT / login) | **Missing** | All routes open |
| OpenAPI / Swagger | **Missing** | |
| Persistent DB (SQLite/Postgres) | **Missing** | |
| Decommission Jinja (migration Phase 3) | **Done** | Templates, form POSTs, Tailwind v3 CSS gone; GET redirects to `/ui/` |
| i18n (Polish in UI + lossless PDF) | **Partial** | PDF: DejaVu if present, else NFKD/latin-1 sanitize |
| Lean production image (no Node/Vite runtime) | **Partial** | `prod` still ships Node so `start_and_seed.sh` can run Vite |
| Frontend unit tests (Jest/RTL) | **Missing** | Playwright only |

## What landed on `feat/decommission-jinja-ui` (2026-09-02)

1. **Search API** (`5b2df09`): `GET /api/recipes?q=&ingredient=` filters via `crud.search_recipes`. Empty both params still lists all.
2. **React recipe search** (`a526cd8`): `RecipeList` search + ingredient filter; Playwright search test.
3. **Jinja HTML gone** (`789212c`): legacy GET paths 302 to `/ui/…`; templates and form POST handlers removed; PDF 404 on missing generated list.
4. **Tailwind v3 CSS pipeline gone** (`e273724`): no `npx tailwindcss@3` in Dockerfile; root `package.json` is a `build:react` wrapper only; `static/css/` deleted.

## Known leftover / dead code

- `frontend/src/components/IngredientDetail.jsx` — unused (route removed). Links to a non-existent `/ingredients/:id/edit`.
- `GET /api/ingredients/info` — unused by current UI (kept for the dead component / future detail).
- `list_unique_locations()` still falls back to raw `location_id`, so datalists can mix `"Dairy"` and `"4"`.
- RecipeForm / ShoppingListView still use several independent `fetch` chains (optional `Promise.all` cleanup).

## Recommended next work (priority)

Jinja decommission is **done**. Remaining work is **not** migration of HTML UI.

1. **Task 7 of the decommission plan** — full Docker verification (`bake dev` + `prod`, pytest, black, pylint, prettier, Playwright including search). Not claimed done in this docs pass.
2. Remove or re-route dead `IngredientDetail.jsx`.
3. Persistent storage (replace in-memory lists).
4. API auth + OpenAPI.
5. Decide on **master ingredients** (real CRUD + persistence) vs keep aggregation-only list.
6. Add missing tests: `/api/ingredients/summary` + `/info`; E2E for ingredients list, standalone list, delete, PDF.
7. Automatic recipe discovery (still the largest unimplemented original feature).
8. Recipe metadata (prep / actual time / shelf life) if those FRs are still desired.
9. Proper i18n (stop relying on PDF sanitization).
10. Lean prod image (drop Node/Vite from the runtime image).
