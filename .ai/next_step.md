# .ai/next_step.md — Handoff

**Branch:** `refactor/abc`
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Codebase review + A/B/C plans committed (`8c20a4a`). **Wave 1 (Plan A) merged** onto `refactor/abc`:

| Task | SHA | What |
|---|---|---|
| A1 | `49ef8d1` | `seed_database()` calls `dao.reset()` |
| A2 | `75c7ddc` | Name-only meal-plan PUT preserves recipes; missing recipe 404; count honored |
| A3 | `a00d80f` | Dropped view-mode purchased checkboxes |
| A4 | `8fe48dd` | MealPlanForm load vs submit errors; `mealPlans.formHint` |
| A5 | `bde1267` | Vite proxies `/shopping-lists` and `/meal-plans` for PDFs |

**A3 decision:** drop checkboxes (do not persist).

## Next

Plan B (`docs/superpowers/plans/2026-09-10-refactor-b-simplification.md`): `api.js`, catalog hook, collapse ingredient GETs, meal-plan names, JSON errors, N+1 `find_all`, E2E hygiene.

Then Plan C. C3 (move `migrate_legacy`) can still run in parallel with B.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
