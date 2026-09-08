# .ai/next_step.md — Handoff

**Branch:** `feat/remove-standalone-shopping-lists-page`
**Last updated:** 2026-09-09

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Removed the standalone Shopping Lists page. Lists live only on a meal plan.

- Dropped `/ui/shopping-lists` route and `nav-shopping-lists`.
- `ShoppingListView` is meal-plan only: generate / edit / PDF / delete. No chooser, switcher, or empty standalone create.
- PDF URL `GET /shopping-lists/<id>/pdf` is unchanged.
- Unused standalone i18n keys removed (en+pl).

Verification:

- `npm run test:unit` in `meal-planner:dev` → **18 passed**
- `lint` / `i18n:check` / `format-check` → clean
- Playwright (isolated `TESTING=true` Vite): shopping-lists.spec.js + main.spec.js `--grep shopping` → **6 passed**

## Next

Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata; meal-plan calendar; meal-plan PDF.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
