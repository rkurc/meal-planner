# .ai/next_step.md — Handoff

**Branch:** `fix/legacy-empty-instructions-and-meal-plan-back`
**Last updated:** 2026-09-04

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Local-run polish after SQLite persistence landed on `main` (#40).

**Legacy CSV import:** `POST /api/recipes` requires non-empty `instructions`. Rows with a blank `przepis` (17 in the USB export, e.g. `placki z kasza kuskus`) 400'd during `migrate_legacy`. `extract_from_csvs` now inserts a placeholder, matching the existing URL-only placeholder. Test: `meal_planner_app/tests/test_migrate_legacy.py`.

**Meal plan detail:** `Back to Meal Plans` link (same pattern as recipes/ingredients), including error/not-found. E2E: `should generate shopping list from meal plan` clicks it and returns to the list.

**Dev start:** `start_and_seed.sh` is executable (`100755`) so bind-mounting source over `/app` no longer hits `permission denied`.

**Not committed:** rebuilt `meal_planner_app/static/react_app/` hashed assets (prod image still `npm run build`s in Docker).

## Next

- Master-ingredient UI CRUD (table exists)
- Auth, OpenAPI, discovery

## Out of scope here

SQLAlchemy, Alembic, multi-worker gunicorn, Postgres adapter.
