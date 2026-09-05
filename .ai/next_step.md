# .ai/next_step.md — Handoff

**Branch:** `chore/i18n-ops-cleanup`
**Last updated:** 2026-09-06

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Cleanup of leftover i18n chrome + ops/quality:

- IngredientForm / IngredientDetail / RecipeForm placeholder hint now use `t()` / `<Trans>` (en+pl keys).
- Stale `.ai/progress.md`, `requirements.md`, `test_plan.md`, `stack.md` refreshed (master ingredients, g↔kg, i18n, lean prod, tests).
- Prod image: no Node, no apt, no `COPY . .`; SPA copied from the frontend-builder stage.
- `dev`/`ci`: Node copied from official `node:*-bullseye` to `/opt/node` (no nodesource + gnupg apt 404). Chromium + nss/nspr baked in; no `playwright install --with-deps`.
- E2E: ingredients CRUD + in-use delete; standalone shopping list + PDF + delete.
- Frontend `node --test src` (leftover chrome scan, shopping grouping) wired in CI.

Verification:
- `docker buildx bake prod --load` → `exporting to image ... naming to docker.io/library/meal-planner:prod`
- prod smoke: Python 3.9.23, gunicorn 23.0.0, no `node`, `/ui/` assets present
- `docker buildx bake ci --load` → Node v20.20.2 from `/opt/node`
- pytest in ci image: **154 passed**
- Playwright in ci image: **15 passed** (12.9s)

## Next

Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata; meal-plan calendar; meal-plan PDF.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
