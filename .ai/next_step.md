# .ai/next_step.md — Handoff

**Branch:** `feat/shopping-list-source-recipe-tooltips`
**Last updated:** 2026-09-09

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Task 2: persist `source_recipe_names` on shopping-list items in SQLite.

- `ShoppingListItem.source_recipe_names: List[str]` (default `[]`).
- `shopping_list_items.source_recipe_names TEXT NOT NULL DEFAULT '[]'` (JSON list of strings; invalid JSON → `[]`).
- Schema v2 migration: existing v1 DBs get `ALTER TABLE` if the column is missing, then `schema_version=2`.
- `create_shopping_list` copies `source_recipe_names` from generated item dicts.
- `update_shopping_list` uses an explicit constructor (missing sources → `[]`); does not splat `**item_data`.

Verification (Docker `meal-planner:dev`):

```
python -m pytest meal_planner_app/tests/test_dao.py \
  meal_planner_app/tests/test_shopping_list_api.py \
  meal_planner_app/tests/test_shopping_list.py -q
```

**48 passed.** New tests failed first (missing field / schema still v1 / API items lacked the key), then passed after implementation. pylint 10.00/10 on changed files.

## Next

Task 3: surface `source_recipe_names` in the shopping-list UI (tooltips).

Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata; meal-plan calendar; meal-plan PDF.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
