> **STANDING INSTRUCTION (for all agents):**
> **Whenever you start a new task, create a new branch first** (see AGENTS.md → "Branching Policy").
> Read this file first, then run `git checkout -b <appropriate-branch-name>` before editing code.

# .ai/next_step.md — Handoff

**Last updated:** 2026-09-03 (PR #38 babysit: Vite `base` fix for nested SPA routes)

## Current branch / code

- **Branch:** `feat/ingredient-default-unit-shopping-list-ui-fixes` (PR #38)
- **Base:** `main`
- **This session:** CI `test-in-container` failed on Playwright deep-link `/ui/recipes/new`.

## What this session did

CI job `test-in-container`: 8/9 Playwright tests passed. The only failure was:

`e2e/main.spec.js:237 › should auto-populate default unit on name change...`

Timeout waiting for `#name` after `page.goto("/ui/recipes/new")`.

**Root cause:** `frontend/vite.config.js` had `base: "./"`. Flask/gunicorn serves the SPA at `/ui/`. A full-page load of `/ui/recipes/new` made the browser resolve `./assets/*.js` as `/ui/recipes/assets/*.js` → 404. Flask catch-all still returned `index.html` (200), so `#name` never appeared. Client-side navigations from `/ui/recipes` still worked (create/edit/delete tests passed).

**Fix:** set Vite `base` to `"/ui/"` so built assets are always `/ui/assets/...`. Plugins, `outDir`, and proxy unchanged. `App.jsx` already has `basename: "/ui"`.

**Verification (Docker, node:20-alpine):**

```bash
docker run --rm -v "$(pwd)/frontend:/app" -w /app node:20-alpine \
  sh -c 'npm ci --no-audit --no-fund --silent && npm run format-check && npm run lint && npx vite build --outDir /tmp/react_build --emptyOutDir'
```

- prettier `--check`: All matched files use Prettier code style
- eslint: clean
- built `index.html` now has `src="/ui/assets/index-C9PrhREh.js"` and CSS `/ui/assets/index-Hp2rs4_N.css`

Full Playwright vs gunicorn was not re-run locally (CI image rebuild is heavy); CI will re-run on push.

## Next steps

1. Wait for PR #38 CI (`test-in-container`) to go green after this push.
2. Do **not** merge from this babysit pass; do **not** touch `feat/decommission-jinja-ui`.
3. Land this branch on `main` only if the default-unit / shopping-list UX is accepted.
4. Remaining product gaps (not this PR): Jinja decommission plan, dead `IngredientDetail.jsx`, persistent DB, auth, OpenAPI.

## Definition of done for *this* fix

- [x] Vite `base` set to `"/ui/"`
- [x] Docker prettier + eslint clean
- [x] Vite production build emits absolute `/ui/assets/` URLs
- [ ] CI Playwright `test-in-container` green (pending this push)
