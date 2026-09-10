# .ai/next_step.md — Handoff

**Branch:** `refactor/abc`
**Last updated:** 2026-09-10
**HEAD:** `refactor/abc` (review fixes after A/B/C)

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Executed the codebase-review plans. **A3 = drop purchased checkboxes.**

| Scope | Tasks | Status |
|---|---|---|
| A Correctness | A1 seed reset, A2 meal-plan PUT, A3 drop checkboxes, A4 MealPlanForm errors, A5 Vite PDF proxy | done |
| B Simplification | B1 api.js, B2 catalog hook, B3 ingredient objects, B4 meal-plan names, B5 JSON errors, B6 batch find_all, B7 E2E hygiene | done |
| C Structural | C1 create_app, C2 split crud, C3 move migrate_legacy, C4 drop recipe_ids + Jinja 302s | done |

Docs: `docs/superpowers/specs/2026-09-10-codebase-review.md` and `docs/superpowers/plans/2026-09-10-refactor-*.md`.

Code review follow-up: `seedDb` asserts HTTP OK; `start_and_seed.sh` exports `TESTING=true`. Playwright **20 passed** against gunicorn + rebuilt SPA (`TESTING=true`).

## Next

- Open a PR from `refactor/abc` against `main`
- Unrelated product work: auth; OpenAPI; calendar; prep-time

## Out of scope

Auth; OpenAI; React Query; SQLAlchemy; persisting purchased checkboxes.
