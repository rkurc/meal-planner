# .ai/next_step.md — Handoff

**Branch:** `refactor/a5-vite-pdf-proxy`
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

A5 (Vite PDF proxy) complete on `refactor/a5-vite-pdf-proxy`.

Vite `server.proxy` now forwards `/api`, `/shopping-lists`, and `/meal-plans` to Flask at `http://127.0.0.1:5000` with `changeOrigin: true`. `/ui` is not proxied (SPA stays on Vite).

Source lock: `frontend/src/vite-proxy.test.js`.

**Verification:**
- FAIL (before impl): `docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev node --test src/vite-proxy.test.js` — assertion failed: only `/api` proxied.
- PASS: `docker run --rm -v "$(pwd)/frontend:/app/frontend" -v /app/frontend/node_modules -w /app/frontend meal-planner:dev npm run test:unit` — 26 pass, 0 fail. Anonymous `node_modules` volume needed so the host mount does not hide image deps (`e2e-workers.test.js` imports `@playwright/test`).
- PASS: `npm run format-check` in the same image (prettier).

## Next

Continue Wave 1 from Plan A (A1 seed reset, A2 meal-plan PUT, A3 drop checkboxes, A4 MealPlanForm errors) if not already done. Then Plan B, then Plan C.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; second DAO backend; persisting purchased checkboxes.
