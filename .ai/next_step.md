# .ai/next_step.md — Handoff

**Branch:** `refactor/b7-e2e-hygiene` (from `refactor/abc`)
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Plan B Task 7 (E2E hygiene):

- Added `frontend/e2e/helpers.js` with `seedDb(page)` (`POST ${API_BASE_URL||http://localhost:5000}/api/test/seed-db`) and `ensureShoppingList(page)` (click Generate if present, else require list; fail if neither).
- `main.spec.js`, `ingredients.spec.js`, `shopping-lists.spec.js` use `seedDb`.
- Removed all `waitForTimeout` from e2e specs (lock: `frontend/src/e2e-timeout.lock.test.js`).
- `page.once("dialog")` registered before save/delete clicks in `main.spec.js`.
- `workers: 1` unchanged (`e2e-workers.test.js`).
- Generate tests assert Edit (via helper) and at least one `shopping-item-sources` item.

Verification (Docker `meal-planner:dev`):

```
docker run --rm \
  -v "$(pwd)/frontend:/app/frontend" \
  -v /app/frontend/node_modules \
  -w /app/frontend meal-planner:dev \
  sh -c 'npm run format-check && npm run lint && npm run test:unit'
```

- format-check: All matched files use Prettier code style
- lint: clean
- test:unit: 35 pass, 0 fail (includes e2e hygiene lock)

Playwright E2E not run (needs gunicorn + `TESTING=true`; do not claim E2E green).

## Next

B3 collapse ingredient GETs, then Plan C.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
