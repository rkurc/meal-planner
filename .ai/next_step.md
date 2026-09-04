# .ai/next_step.md — Handoff

**Branch:** `docs/i18n-design`
**Last updated:** 2026-09-05

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Rebased `docs/i18n-design` onto `origin/main` (`2d88049`). Conflict only in this file. Kept:

- **#42** master-ingredient API and UI CRUD (landed on main)
- **#43** shopping-list location grouping + g↔kg / ml↔l conversion (landed on main)
- **#44** placeholder-instruction UX (banner/badge/edit hash; no scraper) (landed on main)
- This branch's i18n design spec (ready; revised after design review)

**Spec:** `docs/superpowers/specs/2026-09-04-i18n-design.md`

Design-only RFC for i18n (no application code). UI chrome via react-i18next; locale in localStorage; bundle DejaVu + NFC for Polish PDFs; do not auto-translate stored recipes.

Review (`/tmp/grok-omekr/grok-design-review-196bd54a.md`): all 11 issues **addressed**. Contracts now pinned: locale chain is localStorage → navigator only; Playwright `use.locale: 'en-US'` in PR-2; plural-aware `i18n:check` in CI; i18next init copy-pasteable (`escapeValue: false`); PR-1 PDF tests bound (500 on missing font, data-layer purchased-exclusion, NFC qty/unit); merge order strictly PR-1→PR-6; DejaVu is Bitstream Vera (`DejaVu.LICENSE`); KD-9 covers both crud defaults + PDF heading/subtitle.

## Next

Implement i18n in **strict** spec PR order (PDF fonts first):

1. Bundle DejaVu + NFC PDF (lossless Polish; rewrite latin-1 grep test)
2. i18next scaffolding + switcher + nav + Playwright locale pin + `npm run i18n:check` in `ci.yml`
3. Recipe + ingredient chrome
4. Meal plan + shopping chrome (do not change PDF href)
5. PDF `?lang=` + `filename*` + SPA `resolvedLanguage` href
6. Playwright PL smoke + `.ai/progress.md` i18n row → Done for chrome

Unrelated remaining product work: auth; OpenAPI; discovery.

## Out of scope here

Machine-translating ~159 imported recipes; RTL; locales beyond en+pl; Flask-Babel; `/api/config` / env default locale; SQLite locale column; SQLAlchemy; Alembic; multi-worker gunicorn; Postgres adapter.
