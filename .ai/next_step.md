# .ai/next_step.md — Handoff

**Branch:** `feat/recipe-ingest-llm`
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Implemented **recipe ingest from pasted text/HTML** using a small local LLM (Ollama sidecar). URL fetch is intentionally not in this iteration.

Flow: Recipes → Import recipe → paste text/HTML + source URL → `POST /api/recipes/parse` (no DB writes) → review on existing `RecipeForm` → Save via `POST /api/recipes`.

Highlights:

- `meal_planner_app/ingest/`: HTML/JSON-LD extract (stdlib), Ollama `/api/chat` client, parse orchestrator
- JSON-LD Recipe first; 1.5B model only splits ingredient lines or extracts unstructured text
- Case-insensitive catalog name remap; `source_url` is always the user field
- Optional `compose.yaml` profile `llm` (`qwen2.5:1.5b`); prod image stays slim
- UI: `/ui/recipes/import`, en/pl chrome, Playwright intercepts parse (no live model in CI)

### Verification (`meal-planner:dev` / `meal-planner:ci`)

**pytest** — **191 passed**, 17 warnings (PDF `ln=` deprecations, pre-existing):

```
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/ -q --tb=no
```

**pylint** ingest + `main.py` — **10.00/10**

**frontend** — format-check, lint, i18n:check ok; **unit 25 passed / 0 failed** (includes `formDataFromDraft` + RecipeImport leftover-chrome)

**Playwright** (`TESTING=true` gunicorn on :5000, parse route intercepted) — **19 passed**, including `should import a pasted recipe into the create form`

Live Ollama was **not** run (manual: `LLM_BASE_URL=http://ollama:11434 docker compose --profile llm up` then `ollama pull qwen2.5:1.5b`).

## Next

- Manual smoke with real `qwen2.5:1.5b` on a Polish food-blog HTML paste
- Iteration 2: `ingest/fetch.py` + URL field on the import page (same parse contract)
- Unrelated remaining: auth; OpenAPI; prep-time metadata; meal-plan calendar; meal-plan PDF

## Out of scope

URL scraping; cloud LLM fallback; auto-save; fuzzy ingredient merge UI; translating imported recipes.
