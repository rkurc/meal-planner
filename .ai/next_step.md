# .ai/next_step.md — Handoff

**Branch:** `feat/decommission-jinja-ui` (do not switch branches for remaining decommission tasks)
**Last updated:** 2026-09-02

## Standing instruction
Create a new branch only when starting **unrelated** work. This decommission work stays on `feat/decommission-jinja-ui`.

## Context
Phase 3 of `.ai/migration_plan.md`: decommission Jinja so `/ui` React is the only search/list UI. Jinja templates still exist and must not be deleted until later tasks.

## Completed

### Task 1 (prior) — API search filters
Commit `5b2df09`: `GET /api/recipes?q=&ingredient=` filters via `crud.search_recipes`. Empty both params still lists all.

### Task 2 (this) — React recipe search UI + E2E
Commit message: `feat: add recipe search and ingredient filter to React list`

**What landed**
- `RecipeList` reads `q` / `ingredient` from the URL (`useSearchParams`), fetches `/api/recipes` with those params, and keeps the search form visible even when the list is empty or loading (no early return before the form).
- Search inputs: `#recipe-search`, `#ingredient-filter`, submit button **Search**.
- Clear control is a **link** named **Clear** (`getByRole("link", { name: "Clear" })`), shown only when a filter is active; navigates to `/recipes` and clears params.
- Existing `RecipeItem` headings unchanged (`Classic Pancakes` / `Simple Omelette`).
- Basename remains `/ui`.
- Backend not changed in this task.

**TDD**
1. E2E appended first: `should filter recipes by search query and ingredient` in `frontend/e2e/main.spec.js`.
2. Red proven: `#recipe-search` absent from `RecipeList.jsx` before implementation.
3. Implementation then format/lint.

**Verification (Docker-first, no host npm/python)**
- `docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev sh -c 'npm ci --no-audit --no-fund --silent && npm run format && npm run format-check && npm run lint'`
  - Prettier: "All matched files use Prettier code style!"
  - eslint: exit 0
- API smoke (seeded): `q=Pancake` → Classic Pancakes only; `ingredient=Cheese` → Simple Omelette only.
- Playwright (gunicorn `TESTING=true`, `BASE_URL=http://127.0.0.1:5000`, mounted source + `npm run build` so `/ui` served the new bundle):
  - `✓ should filter recipes by search query and ingredient (338ms)` — 1 passed

**Files**
- `frontend/src/components/RecipeList.jsx`
- `frontend/e2e/main.spec.js`
- `.ai/next_step.md` (this)

## Next (later decommission tasks)
Do **not** delete Jinja in this commit. Remaining Phase 3 work (separate tasks):
1. Confirm remaining Jinja-only UI has React parity (meal plans, shopping, recipe CRUD already on `/ui`).
2. Remove Jinja HTML routes in `meal_planner_app/main.py` (keep `/api/*` and `/ui` SPA serving).
3. Delete `meal_planner_app/templates/*.html` and leftover Jinja-only form handling.
4. Point any leftover links/docs at `/ui`; keep E2E on `/ui/` + `BASE_URL=http://localhost:5000`.
5. Re-run full Playwright suite + pytest in Docker after route deletion.

## Out of scope / notes
- Do not push unless asked.
- Do not change backend search contract (`q`, `ingredient`).
- Generated `meal_planner_app/static/react_app/{index.html,assets/}` from local E2E rebuild is untracked; do not commit.
