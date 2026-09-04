# .ai/next_step.md — Handoff

**Branch:** `feat/shopping-list-groups-and-unit-convert`
**Last updated:** 2026-09-05

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Rebased onto `origin/main` after #42 (`e36dabf feat: add master-ingredient API and UI CRUD`). Conflict only in this file; `crud.py` auto-merged. Kept both:

- Master-ingredient CRUD from main (`create_master_ingredient`, API routes, Ingredient UI, `id` on summary)
- Shopping-list unit conversion (`units.py`, `generate_shopping_list` conversion, ShoppingListView grouping)

### Shopping-list polish (this branch)

**Unit conversion (generation only):** `meal_planner_app/units.py` consolidates mass (g/gram(s) ↔ kg/kilogram(s)) and volume (ml/millilitre(s)/milliliter(s) ↔ l/litre(s)/liter(s)). Case-insensitive, trimmed. Identity is name + unit family + location. Mixed g+kg / ml+l: if total ≥ 1000 base units display as kg/l, else g/ml. Same-scale lines keep that scale (0.5 kg stays kg). No g↔ml or count↔mass. Persisted historical lists are not rewritten; `create_shopping_list` from a meal plan stores already-converted units.

**HTML grouping:** `ShoppingListView.jsx` groups the flat persisted `items` array under location headings (empty/missing → "Other"), matching PDF grouping. Purchased checkboxes, edit, and PDF download unchanged. Edit mode stays a flat list with a location field.

**Tests (Docker `meal-planner:dev`, after rebase):**
```
docker run --rm -v "$(pwd):/app" -w /app -e PYTHONPATH=/app meal-planner:dev python -m pytest meal_planner_app/tests/ -q --tb=short
# 138 passed
docker run --rm -v "$(pwd):/app" -w /app -e PYTHONPATH=/app meal-planner:dev python -m black --check meal_planner_app
# All done! 25 files would be left unchanged.
docker run --rm -v "$(pwd):/app" -w /app -e PYTHONPATH=/app meal-planner:dev python -m pylint meal_planner_app
# 10.00/10
```

### Already on main (#42)

Master-ingredient UI CRUD. Catalog rows (`ingredients` table + `IngredientDao`) are a first-class API/UI resource. Recipe get-or-create by name is unchanged.

- `POST /api/ingredients` — trim unique name; optional `default_unit`, `location`, `location_id`. 400 missing name; 409 duplicate.
- `GET /api/ingredients/<uuid>` — detail with `id`, unit, location, usage, recipes.
- `PUT /api/ingredients/<uuid>` — 404 missing; 409 duplicate name.
- `DELETE /api/ingredients/<uuid>` — 404 missing; **409** (JSON `{error, usage_count}`) if `ON DELETE RESTRICT` / dao.delete False.
- `GET /api/ingredients/summary` and `/info` now include `id`. Autocomplete `GET /api/ingredients` stays a string list.
- UI: `/ui/ingredients` catalog list; `/ui/ingredients/:id` detail/edit/delete; `/ui/ingredients/new`.

## Next

- Auth, OpenAPI, discovery
- Optional: E2E for ingredient create/edit/delete (including 409-in-use)
- Optional: rebuild `meal_planner_app/static/react_app/` hashed assets (prod image still `npm run build`s in Docker)

## Out of scope here

Auth, OpenAPI, i18n, recipe-instruction import, SQLAlchemy, Alembic, multi-worker gunicorn, Postgres adapter.
