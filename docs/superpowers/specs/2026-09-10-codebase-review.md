# Codebase review — meal planner

**Date:** 2026-09-10  
**Scope:** `origin/main` @ `c8b480e` (Flask API + SQLite DAO + React `/ui` SPA, including recipe ingest and shopping-list source-recipe names)  
**Decision:** Execute scopes A, then B, then C. **A3 = drop view-mode purchased checkboxes** (do not persist).  
**Plans:** `docs/superpowers/plans/2026-09-10-refactor-{a,b,c}-*.md` and parallelism map `docs/superpowers/plans/2026-09-10-refactor-parallelism.md`.

## Verdict

This is a small, working personal app (~10k lines including tests). Persistence layering is the one sharp boundary and matches the 2026-09-04 DAO design. The rest grew by feature PRs: two god modules, four overlapping ingredient GETs, dual meal-plan payloads, and copy-pasted React pages.

Do **not** rewrite. Do **not** add React Query, SQLAlchemy, a generic CRUD framework, or a second DAO implementation. Prefer thin correctness PRs, then targeted simplification.

Highest-value work is not “cleaner architecture.” It is: seed isolation, a meal-plan PUT that can wipe recipes, purchased checkboxes that do not persist, and collapsing duplicate HTTP/UI paths.

---

## Current architecture

```
Browser  /ui/*     React SPA (Vite, basename /ui)
         /api/*    Flask JSON
         /*/pdf    Flask PDF (not under /api; Vite does not proxy these)

Flask    main.py   routes, serializers, SPA, Jinja-era 302s, test seed
  ↓
App      crud.py   domain ops, search, shopping aggregation (misnamed)
  ↓
Port     dao/      MealPlannerDao protocols
  ↓
SQL      sqlite.py only sqlite3 import; file DB or :memory:
```

| Module | Lines | Actual role |
|---|---|---|
| `crud.py` | 745 | Application layer (recipes, plans, shopping, catalog, search) |
| `migrate_legacy.py` | 718 | One-shot importer (HTTP POST to live API) |
| `main.py` | 657 | Entire Flask app, no factory / blueprints |
| `dao/sqlite.py` | 570 | Persistence |
| `RecipeForm.jsx` | 479 | Recipe create/edit + catalog lookups |
| `ShoppingListView.jsx` | 444 | Embedded shopping editor |
| `tests/test_crud.py` | 552 | Domain tests, search-heavy |
| `tests/test_api.py` | 516 | HTTP + internal `crud` setup |
| `units.py` | 249 | g↔kg / ml↔l consolidation — well bounded |
| `services.py` | 177 | PDF only (name is leftover) |

Frontend is a page-as-component CRUD SPA: no API module, no shared fetch hook, axios only on meal-plan screens, `fetch` everywhere else.

---

## What is already in good shape

- DAO protocols vs SQLite adapter: Flask does not import `sqlite3`; models do not know SQL. Tests inject `:memory:` via `crud.set_dao`.
- Shopping-list **snapshots** (items copied, not live-joined) are the right model for “to-buy.”
- `units.py` is focused and tested.
- Prod image is lean (gunicorn `-w 1`, no Node). Dev/CI complexity is real but intentional (Playwright + Debian).
- Jinja UI is gone. React at `/ui` is the only HTML UI.

---

## Findings

Severity: **bug** (wrong behavior), **smell** (wrong abstraction / duplication that will keep costing), **nit** (cleanup).

### Bugs

**1. Meal-plan PUT with no `recipes` key wipes the plan**  
`api_update_meal_plan` always passes `recipes=_normalize_recipe_entries(...)`. `None` normalizes to `[]`, and `update_meal_plan` treats any non-`None` list as a replacement (`main.py:480–487`, `crud.py:312–313`). Domain `crud.update_meal_plan(name=...)` without `recipes` is tested and preserves entries; the HTTP path is not. Current UI always sends `recipes`, so the form hides it.

**2. `/api/test/seed-db` can leave an empty Weekly Meal Plan**  
`seed_database()` calls `reset_recipes_db()` (delete recipes + catalog only). `meal_plan_recipes` cascades away. The meal-plan **row** remains. `seed_meal_plans()` then skips if a plan named “Weekly Meal Plan” still exists (`seed_db.py:61–88`). Shopping lists are not cleared. `SqliteDao.reset()` already truncates everything and is unused (`dao/sqlite.py:554–567`). This is the same shared-DB class of bug as the Playwright worker race.

**3. Purchased checkboxes do not persist — DROPPED (A3)**  
View-mode toggles only mutated `editedItems` and never PUT. **Decision: remove the checkboxes** (and `handleTogglePurchased`) rather than persist them. Keep `purchased: false` on new edit-mode rows so the API snapshot field still round-trips. Keep source-recipe tooltips on the item label.

**4. MealPlanForm submit errors unmount the form**  
`setError` from `handleSubmit` hits the same `if (error) return … Error loading form` branch used for fetch failure (`MealPlanForm.jsx:128–143`). IngredientForm already does this correctly (inline banner).

**5. Add-recipe-to-plan is a no-op 200 when the recipe is missing**  
`add_recipe_to_meal_plan` returns the unchanged plan if the recipe does not exist (`crud.py:257–264`). The route treats only a missing **plan** as 404 (`main.py:509–513`). `count` is never read from JSON.

**6. Vite PDF 404 in local dev**  
PDF links are `/shopping-lists/<id>/pdf` (not `/api`). Vite proxies only `/api` (`vite.config.js:14–19`). CI works because Playwright hits Flask `:5000`.

### Wrong abstraction / layering

**God modules, not extra layers.** `crud.py` is the real application service; `services.py` is PDF. Callers still talk to `crud.*`. Splitting `crud` by aggregate (recipes / meal plans / shopping / ingredients) is enough. Do not insert another “service layer.”

**Flask is a 657-line route file.** Serializers, Jinja 302s, SPA catch-all, PDF HTTP, and the test seed live together. No `create_app()`. DAO is a process singleton (`crud.get_dao`), so `check_same_thread=False` is required.

**Protocol/factory is slightly ahead of a single SQLite backend, but cheap.** Keep it. Do not add Postgres or SQLAlchemy “for later.”

**Anemic models are fine at this size.** Inconsistency is the problem: `ShoppingList` is a dataclass; `Recipe` / `MealPlan` / `Ingredient` are hand-written; meal-plan entries are `List[Dict]` with both `id` and `recipe_id`.

**Frontend copy-paste is the wrong level.** Three CRUD resources share list/detail/form shells. RecipeForm and ShoppingListView clone four catalog fetches and the default-unit autofill. A `api.js` + `useCatalogLookups()` + ingredient row is the right extract. A generic `<EntityCrud>` / React Query is not.

### Inefficiencies (fine for seed size; wrong if the catalog grows)

- `RecipeDao.find_all` is N+1 (one query per recipe for lines). Same pattern for meal plans and shopping lists.
- `search_recipes` loads all recipes, then `get_recipe` again per match (`crud.py:565–585`).
- `list_ingredients_summary` and `_master_ingredient_to_dict` scan every recipe for usage instead of `GROUP BY ingredient_id`.
- `list_unique_units` hydrates every recipe for unit strings.
- Meal-plan detail: GET plan + GET **all** recipes (client join) + GET **all** shopping lists (`.find` by `meal_plan_id`) + four lookup GETs. StrictMode doubles that.
- `GET /api/ingredients` (names) **and** `/api/ingredients/summary` on the same screens; summary already has names.

### Overlapping / dead API

| Endpoint | Status |
|---|---|
| `GET /api/ingredients` | `string[]` for autocomplete |
| `GET /api/ingredients/summary` | list objects (what the list page needs) |
| `GET /api/ingredients/info?name=` | unused by UI; tests only |
| `GET /api/ingredients/<uuid>` | detail by id |
| Meal-plan JSON `recipes` **and** `recipe_ids` | UI still sends both |
| `GET /api/meal-plans/<id>/shopping-list` | grouped generate; UI uses persisted lists |
| Jinja GET 302s in `main.py:67–109` | bookmark compat only |
| `location` + `location_id` everywhere | no locations table; recipe-line location is **not stored** (JOIN from master) |

`POST /api/ingredients` creates an object on the same path GET uses for a string list.

### Frontend smells

- Mixed `fetch` vs `axios`. MealPlanForm reads FastAPI-shaped `error.response?.data?.detail`; Flask `abort()` does not produce that.
- Hardcoded English errors/alerts while i18n keys already exist (`mealPlans.formHint`, `recipes.failedSave`).
- `key={index}` on dynamic ingredient/plan rows.
- Nested `container mx-auto p-4` (Layout already wraps).
- `eslint` `no-unused-vars` off; unused `mealPlanName` prop.
- No abort / ignore-stale on list fetches.

### Tests / infra / docs

- Native CI pytest + bake `ci` + **bake `ci` again** in the integration workflow. Chromium is installed in the image and reinstalled in the job.
- E2E `workers: 1` is a bandage on shared SQLite + seed-db. Incomplete seed (finding 2) is the real isolation bug.
- Duplicate coverage: unit merge in `test_units.py` **and** `test_shopping_list.py`; search in crud + API + E2E.
- No Playwright for meal-plan create/edit; no RTL for forms.
- `.gitignore` lists `frontend/package-lock.json` while Docker `npm ci` requires it (file is tracked; the ignore line is a footgun).
- README still says prod includes Node + Vite (`README.md` production section). Prod CMD is gunicorn only.
- `migrate_legacy.py` (~700 lines) lives in the runtime package; `.odb` heuristic is untested; CSV is the documented path.

---

## What not to do

- Rewrite Flask → FastAPI / SQLAlchemy / Postgres “while we’re here.”
- Generic CRUD component or React Query before a 20-line `api.js`.
- Second DAO implementation to “prove” the protocol.
- Growing `services.py` into a real service layer. Rename it to `pdf.py` instead.
- Dropping E2E `workers: 1` before seed calls `dao.reset()`.

---

## Refactoring scopes (choose one)

### A — Correctness (in progress)

1. Seed: `dao.reset()` then always recreate Weekly Meal Plan; pytest that a second seed still has recipes on the plan.
2. Meal-plan PUT: apply `recipes` only if the key is present; 404 on add-missing-recipe; pass `count`.
3. **Drop view-mode purchased checkboxes** (chosen). Keep source-recipe tooltips.
4. MealPlanForm: inline submit errors; use existing `mealPlans.formHint`.
5. Vite proxy for PDF paths.

**Effort:** a few small PRs. **Risk:** low. Unblocks later cleanup.

### B — Targeted simplification (after A)

Remove duplication without moving boxes.

1. Frontend `api.js` + drop axios.
2. `useCatalogLookups()` + shared ingredient row; stop double-fetching names + summary.
3. Collapse ingredient GETs: list returns objects; delete `/info` (UI-unused); usage via SQL `GROUP BY`.
4. Meal-plan JSON includes recipe `name`; drop the “fetch all recipes” join.
5. JSON error handler for `/api/*`.
6. Kill search/list N+1 inside SQLite (`find_all` batch lines).
7. E2E: shared `seedDb()`, drop `waitForTimeout`, stop double-building `ci` if cheap.

**Effort:** several PRs. **Risk:** medium (API consumers + Playwright selectors).

### C — Structural (only if B is the steady state you want)

1. `create_app(testing=False)`; register seed route only when testing; bind DAO to the app.
2. Split `crud.py` by aggregate; re-export from `crud` for one release; rename `services.py` → `pdf.py`.
3. Quarantine `migrate_legacy` out of the runtime package; drop `.odb` if CSV is canonical.
4. Drop `recipe_ids` from JSON once frontend grep is clean; drop Jinja 302s after a grace period.

**Effort:** high churn, low user-visible value. **Risk:** every test imports `app`. Do not start here.

---

## Execution

See `docs/superpowers/plans/2026-09-10-refactor-parallelism.md`. Wave 1 (A1–A5) can run in parallel on isolated worktrees. B waits on A. C waits on B except C3 (quarantine `migrate_legacy`), which is independent.
