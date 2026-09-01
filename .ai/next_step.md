# .ai/next_step.md — Handoff

**Branch:** `feat/decommission-jinja-ui` (do not switch branches for remaining decommission verification)
**Last updated:** 2026-09-02

## Standing instruction
Create a new branch only when starting **unrelated** work. Decommission verification (Task 7) stays on `feat/decommission-jinja-ui`.

## Context
Phase 3 of `.ai/migration_plan.md` is **complete**. React at `/ui/` is the only HTML UI. Jinja templates, form POSTs, and the Tailwind v3 CSS pipeline are gone. Recipe search is API + React. Canonical status: `.ai/progress.md`.

## Completed

### Task 1 — API search filters
Commit `5b2df09`: `feat: filter GET /api/recipes with q and ingredient query params`

### Task 2 — React recipe search UI + E2E
Commit `a526cd8`: `feat: add recipe search and ingredient filter to React list`

### Tasks 3+4 — Legacy GET redirects + remove Jinja
Commit `789212c`: `feat: decommission Jinja UI; redirect legacy GET paths to /ui/`

### Task 5 — Remove Jinja Tailwind v3 CSS pipeline
Commit `e273724`: `chore: remove Jinja Tailwind v3 CSS pipeline`

`docker buildx bake prod` succeeded (~42s); no `tailwindcss@3` / `input.css` / `output.css` step.

### Task 6 — Docs + progress trackers (this)
Commit: `docs: mark Jinja decommission complete; React is the only HTML UI`

Updated `.ai/progress.md` (canonical, 2026-09-02), migration/implementation/feature/test/stack/requirements, `README.md`, `meal_planner_app/README.md`, and the decommission plan checklist. Next work is **not** Jinja.

## Next (not Jinja)

1. **Task 7 — full verification** of `docs/superpowers/plans/2026-09-01-jinja-decommission.md` (definition of done). Do **not** claim it until observed:
   - `docker buildx bake dev` and `prod` DONE
   - pytest all green in the dev image (83 tests in tree)
   - black `--check`, pylint 10.00/10
   - frontend format-check + lint
   - Playwright including the search test (10 E2E)
   - `rg render_template meal_planner_app` has no `main.py` hits
   - `GET /` 302 `/ui/`
   - persisted shopping-list PDF still starts with `%PDF`
2. After that, **unrelated** follow-ups (new branch when leaving decommission):
   - Persistent DB (in-memory store still loses data on restart)
   - Auth + OpenAPI
   - Dead `IngredientDetail.jsx` (no route) / unused `GET /api/ingredients/info`
   - E2E gaps: ingredients page, standalone lists, delete, PDF click
   - Master ingredients / discovery (new features, not migration)

## Out of scope / notes
- Do not push unless asked.
- Keep `/ui` basename.
- Keep both PDF routes.
- Do not restore POST form aliases.
- Do not restore Tailwind v3 / Jinja CSS or templates.
- Do not claim Task 7 done from this docs commit.
