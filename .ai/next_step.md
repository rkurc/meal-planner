# .ai/next_step.md — Handoff

**Branch:** `feat/master-ingredient-ui-crud`
**Last updated:** 2026-09-04

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Master-ingredient UI CRUD. Catalog rows (`ingredients` table + `IngredientDao`) are now a first-class API/UI resource. Recipe get-or-create by name is unchanged.

**API**
- `POST /api/ingredients` — trim unique name; optional `default_unit`, `location`, `location_id`. 400 missing name; 409 duplicate.
- `GET /api/ingredients/<uuid>` — detail with `id`, unit, location, usage, recipes.
- `PUT /api/ingredients/<uuid>` — 404 missing; 409 duplicate name.
- `DELETE /api/ingredients/<uuid>` — 404 missing; **409** (JSON `{error, usage_count}`) if `ON DELETE RESTRICT` / dao.delete False.
- `GET /api/ingredients/summary` and `/info` now include `id`. Autocomplete `GET /api/ingredients` stays a string list.

**UI**
- `/ui/ingredients` — catalog list; "Add ingredient" → `/ingredients/new`.
- `/ui/ingredients/:id` — detail, edit, delete with confirm; 409 shows "still used by N recipes".
- `/ui/ingredients/:id/edit` and `/ingredients/new` — name, default_unit, location (datalist from `/api/locations`).

**Tests (Docker)**
```
docker run --rm -v "$(pwd):/app" -w /app -e PYTHONPATH=/app meal-planner:dev python -m pytest meal_planner_app/tests/ -q --tb=short
# 113 passed
docker run --rm -v "$(pwd):/app" -w /app -e PYTHONPATH=/app meal-planner:dev python -m black --check meal_planner_app
docker run --rm -v "$(pwd):/app" -w /app -e PYTHONPATH=/app meal-planner:dev python -m pylint meal_planner_app
# 10.00/10
```
Frontend prettier + eslint on changed files via `meal-planner:dev`.

## Next

- Auth, OpenAPI, discovery
- Optional: E2E for ingredient create/edit/delete (including 409-in-use)
- Optional: rebuild `meal_planner_app/static/react_app/` hashed assets (prod image still `npm run build`s in Docker)

## Out of scope here

Auth, OpenAPI, i18n, shopping-list grouping, recipe-instruction import, SQLAlchemy, Alembic, multi-worker gunicorn, Postgres adapter.
