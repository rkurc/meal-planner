# .ai/next_step.md — Handoff

**Branch:** `feat/shopping-list-source-recipe-tooltips`
**Last updated:** 2026-09-09

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Task 1: aggregate unique recipe names at generate time (names only, first-seen order; not persisted).

- `add_to_aggregate(..., recipe_name="")` records unique `source_recipe_names` on each bucket.
- `_item_dict` / `_finalize_entry` include `source_recipe_names` on generated item dicts.
- `generate_shopping_list` passes `recipe_name=recipe.name or ""`.
- SQLite persistence and frontend are unchanged (Task 2 / later).

Verification (Docker `meal-planner:dev`):

```
python -m pytest meal_planner_app/tests/test_units.py \
  meal_planner_app/tests/test_shopping_list.py -q
```

**33 passed** (new tests failed first on missing `recipe_name` / `source_recipe_names`, then passed after the implementation).

## Next

Task 2: persist `source_recipe_names` on shopping-list items in SQLite.

Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata; meal-plan calendar; meal-plan PDF.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
