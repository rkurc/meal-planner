# .ai/next_step.md — Handoff

**Branch:** `fix/e2e-serial-workers`
**Last updated:** 2026-09-09

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Fixed failing `main` Integration/E2E job (run 34292239075 on `aca77be`).

Root cause: Playwright defaulted to multiple workers. Every spec `beforeEach` POSTs `/api/test/seed-db`, which **resets** the shared SQLite DB and mints new recipe IDs. Parallel workers raced that reset:

- #50 (`aca77be`): `should edit an existing recipe` → `#description` timeout, page was **Error: Recipe not found**
- #49 (`ad8bb52`): `should create, edit, and delete a master ingredient` → `waitForURL` timeout
- #48 passed (same flake, lucky schedule)

Fix:

- `frontend/playwright.config.js`: `workers: 1`
- `.github/workflows/integration-tests.yml`: `npx playwright test --workers=1`
- `frontend/src/e2e-workers.test.js` locks the config value

Verification (Docker):

- `meal-planner:dev` `npm run test:unit` → **15 passed** (includes workers lock)
- `format-check` / `lint` / `i18n:check` → clean
- `meal-planner:ci` Playwright `--workers=1` → **16 passed**, including `should edit an existing recipe` and `should create, edit, and delete a master ingredient`

## Next

Merge `fix/e2e-serial-workers` once CI is green. Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata; meal-plan calendar; meal-plan PDF.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
