# .ai/next_step.md — Handoff

**Branch:** `feat/fill-empty-recipe-instructions`
**Last updated:** 2026-09-05

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Rebased onto `origin/main` (`edac188` — #43 shopping-list grouping/units, which already includes #42 master-ingredient CRUD). Conflict only in this file. Kept both:

- Ingredient CRUD UI/API from main (`create_master_ingredient`, API routes, Ingredient UI, `id` on summary)
- Shopping list grouping + `units.py` from main (`generate_shopping_list` conversion, ShoppingListView grouping)
- This branch's placeholder-instruction UX (see below)

### Placeholder-instruction UX (this branch)

UX to help users fill empty / placeholder recipe instructions after legacy CSV import.

**Detection:** `frontend/src/hasPlaceholderInstructions.js` treats empty, whitespace-only, and known `migrate_legacy` placeholders as missing steps (the two przepisy CSV strings plus older .odb / generic CSV variants). Does not change `migrate_legacy.py` placeholder text.

**Recipe detail:** placeholder instructions are no longer shown as if they were real steps. Amber banner (`missing-instructions-banner`) + "Edit instructions" (to `/recipes/:id/edit#instructions`). If `source_url` is set, prominent "Open source recipe" (new tab).

**Recipe list:** subtle "Needs instructions" badge on cards that still need steps.

**Recipe form:** autofocus + scroll to instructions when hash is `#instructions` or the loaded text is a placeholder; helper copy with source link. No fetch/scraper (CORS / HTML soup).

**Tests (Docker `meal-planner:dev`, after rebase onto `edac188`):**
```
docker run --rm -v "$(pwd):/app" -w /app -e PYTHONPATH=/app meal-planner:dev python -m pytest meal_planner_app/tests/ -q --tb=short
# 138 passed
docker run --rm -v "$(pwd):/app" -w /app -e PYTHONPATH=/app meal-planner:dev python -m black --check meal_planner_app
# All done! 25 files would be left unchanged.
docker run --rm -v "$(pwd):/app" -w /app -e PYTHONPATH=/app meal-planner:dev python -m pylint meal_planner_app
# 10.00/10
```
Frontend prettier + eslint clean on changed files; `npm run test:unit` 5/5.
Playwright: `should highlight placeholder instructions and offer source + edit` creates a recipe with the CSV placeholder via the existing form + `/api/test/seed-db` beforeEach. Seeded recipes must not show the banner/badge. Playwright not executed here (no app servers).

### Already on main (#42, #43)

Master-ingredient UI CRUD and shopping-list location grouping + g↔kg / ml↔l conversion. Unchanged by this rebase.

## Next

- Open PR against main (stacked after #42 and #43)
- Auth, OpenAPI, discovery
- Optional: E2E for ingredient create/edit/delete (including 409-in-use)
- Optional: rebuild `meal_planner_app/static/react_app/` hashed assets (prod image still `npm run build`s in Docker)
- Run Playwright against a seeded stack (`BASE_URL` + `API_BASE_URL`) to confirm the new e2e

## Out of scope here

Automatic Recipe Discovery (web search / NLP / HTML scrape). Auth, OpenAPI, i18n, SQLAlchemy, Alembic, multi-worker gunicorn, Postgres adapter.
