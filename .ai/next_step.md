# .ai/next_step.md — Handoff

**Branch:** `refactor/abc`
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Executed plans A and B, plus C1/C3/C4. Remaining: **C2 split crud.py**.

Done on this branch (from `origin/main` @ `c8b480e`):

- A1 seed `dao.reset()`; A2 meal-plan PUT/add-recipe; A3 drop purchased checkboxes; A4 MealPlanForm errors; A5 Vite PDF proxy
- B1 `api.js` / drop axios; B2 catalog hook + line fields; B3 ingredient GET objects; B4 meal-plan names; B5 JSON /api errors; B6 batch find_all; B7 E2E seedDb / no waitForTimeout
- C1 `create_app()` opt-in seed route; C3 `tools/migrate_legacy.py`; C4 drop `recipe_ids` JSON + Jinja 302s

**A3 decision:** drop checkboxes (do not persist).

## Next

Plan C Task 2: split `crud.py` into `domain/*` with compatibility re-export; rename `services.py` → `pdf.py`.

Then finishing-a-development-branch (PR / merge options).

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
