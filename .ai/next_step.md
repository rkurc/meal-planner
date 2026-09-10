# .ai/next_step.md — Handoff

**Branch:** `feat/recipe-ingest-url-fetch`
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

PR #53 (paste + local LLM ingest) merged to `main` as `3bd1b23`. Backend CI had failed on pylint C0415; fixed in `0dd0851` before merge.

Iteration 2: **URL scraping**. `ingest/fetch.py` downloads a public page; Import can Fetch page into the textarea or Parse with only a URL. Same review-in-RecipeForm save path. SSRF: no localhost/private/link-local/metadata IPs.

### Verification

- pylint `meal_planner_app` **10.00/10**, exit 0
- pytest **205 passed**
- frontend format/lint/i18n + unit **25 passed**
- Playwright **20 passed**, including `should fetch a recipe URL then parse it`

## Next

- Merge PR for `feat/recipe-ingest-url-fetch`
- Manual smoke: real Ollama + a public Polish recipe URL
- Unrelated remaining: auth; OpenAPI; prep-time metadata; meal-plan calendar; meal-plan PDF

## Out of scope

Cloud LLM fallback; auto-save; fuzzy ingredient merge; JS-rendered-only pages (no headless browser).
