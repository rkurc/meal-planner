# .ai/next_step.md — Handoff

**Branch:** `docs/i18n-design`
**Last updated:** 2026-09-05

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Rebased `docs/i18n-design` onto `origin/main` (`2d88049`), which now includes:

- **#42** master-ingredient API and UI CRUD
- **#43** shopping-list location grouping + g↔kg / ml↔l conversion
- **#44** placeholder-instruction UX (banner/badge/edit hash; no scraper)

Conflict only in this file. Kept main's landed features and this branch's i18n design spec.

**Spec:** `docs/superpowers/specs/2026-09-04-i18n-design.md`

Design-only RFC for i18n (no application code). UI chrome via react-i18next; locale in localStorage; bundle DejaVu + NFC for Polish PDFs; do not auto-translate stored recipes.

Verified in tree: React chrome is hardcoded English (`frontend/src/components/*.jsx`); no `react-i18next` / Flask-Babel; PDF (`meal_planner_app/services.py`) uses system DejaVu if present else NFKD/latin-1 sanitization (DejaVu path still NFKD-decomposes). User content from legacy Polish CSV is **not** auto-translated in v1.

## Next

Implement i18n in the spec **PR Plan** order (PDF fonts first):

1. Bundle DejaVu + NFC PDF (lossless Polish) — independently valuable
2. i18next scaffolding + locale switcher + nav (en/pl)
3. Recipe + ingredient chrome
4. Meal plan + shopping chrome
5. PDF `?lang=` chrome + `filename*`
6. Playwright PL smoke + `.ai/progress.md` i18n row → Done for chrome

Unrelated remaining product work: auth; OpenAPI; discovery.

## Out of scope here

Machine-translating ~159 imported recipes; RTL; locales beyond en+pl; Flask-Babel; SQLite locale column; SQLAlchemy; Alembic; multi-worker gunicorn; Postgres adapter.
