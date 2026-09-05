# .ai/next_step.md — Handoff

**Branch:** `fix/pdf-bundle-dejavu-nfc`
**Last updated:** 2026-09-05

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

i18n spec **PR-1**: lossless Polish shopping-list PDFs.

- Vendor DejaVu Sans + Bold (Debian `fonts-dejavu-core` / DejaVu **2.37**) under `meal_planner_app/static/fonts/` with `DejaVu.LICENSE` (Bitstream Vera, not OFL).
- Resolve bundled TTF via `importlib.resources` (plus `Path(__file__)` fallback; added `meal_planner_app/__init__.py` so the package is not a namespace).
- System DejaVu path is spare. Missing both → `FontUnavailableError` → Flask **500**. No Helvetica, no `sanitize_for_pdf`.
- All drawn user text is **NFC** (name, quantity, unit, location, title). Empty-list copy goes through the Unicode font.
- Title is English chrome heading **"Shopping List"** plus stored name subtitle (KD-9; no `Shopping List for:` prefix).
- Tests: `meal_planner_app/tests/test_pdf.py`; purchased-exclusion asserts `shopping_list_to_pdf_data` (not latin-1 PDF grep).
- `.dockerignore`: `!meal_planner_app/static/fonts/`

**Verification (Docker `meal-planner:dev`, PYTHONPATH=/app):**
- pytest: **152 passed**
- black `--check`: clean
- pylint: **10.00/10**

## Next (i18n spec PR-2)

i18next scaffolding + locale switcher + nav + Playwright `use.locale: 'en-US'` + `npm run i18n:check` in `ci.yml`.

Then PR-3 recipe chrome, PR-4 shopping chrome, PR-5 `?lang=` / `filename*`, PR-6 PL E2E smoke.

## Out of scope here

`?lang=` / `filename*` / `pdf_strings.py` (PR-5); react-i18next; translating stored recipes.
