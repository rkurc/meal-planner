# .ai/next_step.md — Handoff

**Branch:** `feat/decommission-jinja-ui` (do not switch branches for remaining decommission tasks)
**Last updated:** 2026-09-02

## Standing instruction
Create a new branch only when starting **unrelated** work. This decommission work stays on `feat/decommission-jinja-ui`.

## Context
Phase 3 of `.ai/migration_plan.md`: decommission Jinja so `/ui` React is the only HTML UI. Legacy GET paths now 302 into `/ui/…`. Templates, form POST handlers, and the leftover Tailwind v3 CSS pipeline are gone.

## Completed

### Task 1 (prior) — API search filters
Commit `5b2df09`: `GET /api/recipes?q=&ingredient=` filters via `crud.search_recipes`. Empty both params still lists all.

### Task 2 (prior) — React recipe search UI + E2E
Commit `a526cd8`: `feat: add recipe search and ingredient filter to React list`

### Tasks 3+4 (prior) — Legacy GET redirects + remove Jinja
Commit `789212c`: `feat: decommission Jinja UI; redirect legacy GET paths to /ui/`

### Task 5 (this) — Remove Jinja Tailwind v3 CSS pipeline
Commit message: `chore: remove Jinja Tailwind v3 CSS pipeline`

**What landed**
- Deleted Dockerfile `RUN` that built leftover Tailwind v3 (`npx … -p tailwindcss@3` against `meal_planner_app/static/css/src/input.css` → `dist/output.css`).
- Slimmed root `package.json` to a convenience `build:react` wrapper. Nothing in CI/Docker called root `npm run build` (CI frontend job and Dockerfiles use `frontend/` + `npm run build` / Vite). Dropped root `tailwindcss`/`postcss`/`autoprefixer` (frontend already has Tailwind 4).
- Deleted `meal_planner_app/static/css/` (`src/input.css`; no committed `dist/`).
- `pyproject.toml` package-data is now `meal_planner_app = ["static/**/*"]` (dropped `templates/**/*`).

**Verification**
- `docker buildx bake prod` — exit 0, **~42s**
- Frontend CSS is Vite/Tailwind 4 only: `RUN npm run build` → `vite build` → `index-….css`
- Log has **no** `tailwindcss@3`, `input.css`, or `output.css` step
- Final stage after `npm ci` is `WORKDIR /app` then `chown` (legacy CSS RUN gone)
- Export: `naming to docker.io/library/meal-planner:prod` / `exporting to image` **DONE**
  - image: `sha256:81a6d917df003fef3a2605353892be5636655afe161d77705df67abe85c8b2e9`

**Files**
- `Dockerfile`
- `package.json`
- `pyproject.toml`
- `meal_planner_app/static/css/` (deleted)
- `.ai/next_step.md` (this)

## Next (remaining decommission tasks)
Do **not** switch branches. Remaining work (separate tasks):
1. **Task 6 — docs rewrite:** README, `.ai/*.md`, stack/requirements still describe dual Jinja+React UI. Also leftover ignore comments for `meal_planner_app/static/css/dist/` in `.gitignore` / `.dockerignore` if you want them cleaned while touching docs.
2. Re-run full Playwright suite in Docker against `/ui/` after these backend route changes (pytest already green).

## Out of scope / notes
- Do not push unless asked.
- Keep `/ui` basename.
- Keep both PDF routes.
- Do not restore POST form aliases.
- Do not restore Tailwind v3 / Jinja CSS.
