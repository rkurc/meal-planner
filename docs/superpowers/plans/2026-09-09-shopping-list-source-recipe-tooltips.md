# Shopping list source-recipe tooltips

> **Status (2026-09-10):** Implemented and verified on `feat/shopping-list-source-recipe-tooltips`. Feature HEAD `02ccf38`. Task 5 full checks green (pytest 160, frontend unit 21 + lint/i18n/format, pre-commit, Playwright shopping-lists 4/4).

**Goal:** When a shopping-list item is aggregated from meal-plan recipes, show the source recipe names on hover so the cook can see *why* an ingredient is on the list.

## What landed

1. **Aggregate** (`ee7ba8b`) — `meal_planner_app/units.py` attaches unique `source_recipe_names` while consolidating compatible units.
2. **Persist** (`001172a`) — `ShoppingListItem.source_recipe_names` is stored (SQLite JSON text, schema v2 `ADD COLUMN`), returned by CRUD/API, preserved on PUT.
3. **Tooltip UI** (`10a1603`) — `ShoppingListView` sets `title` from `formatSourceRecipeNames(...)` and `data-testid="shopping-item-sources"` when names exist.
4. **E2E** (`256c5d6`, `02ccf38`) — `generated items show source recipe names on hover title` requires Generate after leftover lists are deleted, fails closed if shopping-lists GET is not ok, asserts Flour `title="Classic Pancakes"`.

## Verification (Task 5)

Docker-first, `docker.exe`, volumes `$(wslpath -w "$(pwd)")`:

| Check | Image | Result |
|---|---|---|
| `python -m pytest meal_planner_app/tests/ -q --tb=no` | `meal-planner:dev` | **160 passed**, 17 warnings, 1.81s |
| `npm run test:unit && lint && i18n:check && format-check` | `meal-planner:dev` | **21 passed**; lint/i18n/prettier ok |
| `python -m pre_commit run --all-files` | `meal-planner:dev` | all hooks **Passed** (after trailing-whitespace on 3 unrelated files) |
| Playwright `e2e/shopping-lists.spec.js --workers=1` | `meal-planner:ci` + gunicorn `TESTING=true` `-w 1` | **4 passed (6.6s)** |

See `.ai/next_step.md` for the exact commands.

## Not in this branch

Auth; OpenAPI; recipe discovery; prep-time metadata; meal-plan calendar; meal-plan PDF.
New branch only for unrelated work.
