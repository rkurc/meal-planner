# .ai/next_step.md — Handoff

**Branch:** `feat/decommission-jinja-ui` (do not switch branches for remaining decommission tasks)
**Last updated:** 2026-09-02

## Standing instruction
Create a new branch only when starting **unrelated** work. This decommission work stays on `feat/decommission-jinja-ui`.

## Context
Phase 3 of `.ai/migration_plan.md`: decommission Jinja so `/ui` React is the only HTML UI. Legacy GET paths now 302 into `/ui/…`. Templates and form POST handlers are gone.

## Completed

### Task 1 (prior) — API search filters
Commit `5b2df09`: `GET /api/recipes?q=&ingredient=` filters via `crud.search_recipes`. Empty both params still lists all.

### Task 2 (prior) — React recipe search UI + E2E
Commit `a526cd8`: `feat: add recipe search and ingredient filter to React list`

### Tasks 3+4 (this) — Legacy GET redirects + remove Jinja
Commit message: `feat: decommission Jinja UI; redirect legacy GET paths to /ui/`

**What landed**
- TDD: redirect tests added first; `TestApi::test_root_redirects_to_ui` failed `200 != 302` while Jinja still rendered.
- GET-only 302s: `/` → `/ui/`; `/recipes`, `/recipes/new`, `/recipes/<id>`, `/recipes/<id>/edit`; `/meal-plans`, `/meal-plans/new`, `/meal-plans/<id>`, `/meal-plans/<id>/edit`.
- Shopping HTML GET `/meal-plans/<id>/shopping-list` → `/ui/meal-plans/<id>` (not a shopping-list path).
- No POST form aliases (`/recipes/new`, `/delete`, `/add-recipe`, etc.).
- Deleted `nl2br`, `parse_ingredients_from_textarea`, and all Jinja HTML handlers (`recipe_list` through `shopping_list_detail_route`).
- Deleted `meal_planner_app/templates/` (8 HTML files).
- Failed meal-plan PDF (`generate_shopping_list` is None) now `abort(404)` instead of redirecting to deleted HTML.
- Kept: `remove_trailing_slash`, `_pdf_attachment_response`, both PDF routes (`/meal-plans/<id>/shopping-list/pdf` and `/shopping-lists/<id>/pdf`), `/api/*`, `/ui` catch-all.
- Dropped unused imports: `render_template`, `url_for`, `Markup`, `escape`. `render_template` is gone from `main.py`.
- Removed form POST tests: `test_create_recipe_via_form`, `test_edit_recipe_via_form`, `test_delete_recipe_via_form`, `test_create_meal_plan_via_form`, `test_generate_shopping_list_route`.

**Verification (Docker-first, `meal-planner:dev`)**
- Red: `pytest meal_planner_app/tests/test_api.py::TestApi::test_root_redirects_to_ui` → `AssertionError: 200 != 302`
- Green: `python -m pytest meal_planner_app/tests/ -q --tb=short` → **83 passed**, 4 warnings (fpdf2 `ln` deprecation in PDF tests)
- Redirect tests 302; PDF tests still 200 `application/pdf`
- `python -m black .` — 15 files unchanged after format
- `python -m pylint --rcfile=.pylintrc meal_planner_app` — **10.00/10**
  - `TestApi` has `# pylint: disable=too-many-public-methods` (21 methods / 20 default) so redirect tests stay on `TestApi` as specified.

**Files**
- `meal_planner_app/main.py`
- `meal_planner_app/tests/test_api.py`
- `meal_planner_app/templates/*.html` (deleted)
- `.ai/next_step.md` (this)

## Next (remaining decommission tasks)
Do **not** switch branches. Remaining work (separate tasks):
1. **Task 5 — CSS pipeline:** drop leftover Jinja Tailwind/PostCSS build in `Dockerfile` (comment still says "legacy Tailwind CSS for old Jinja templates"). Keep React/Vite CSS.
2. **Task 6 — docs rewrite:** README, `.ai/*.md`, `pyproject.toml` package-data `templates/**/*`, stack/requirements still describe dual Jinja+React UI.
3. Re-run full Playwright suite in Docker against `/ui/` after these backend route changes (pytest already green).

## Out of scope / notes
- Do not push unless asked.
- Keep `/ui` basename.
- Keep both PDF routes.
- Do not restore POST form aliases.
