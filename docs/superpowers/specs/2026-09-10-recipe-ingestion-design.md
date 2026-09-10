# Recipe ingestion (paste text/HTML + local LLM)

**Date:** 2026-09-10  
**Status:** Approved for implementation  
**Branch:** `feat/recipe-ingest-llm`

## Goal

Lower the cost of adding a recipe: the user pastes free text or scraped HTML/XML plus a source URL, a small local LLM turns that into structured fields, and the existing create-recipe form is pre-filled for review. Saving uses today's `POST /api/recipes` path (get-or-create master ingredients, then recipe lines + steps + source).

A later iteration adds a URL fetcher. This design leaves a clean seam for that without implementing fetch now.

## Product decisions

- After parse: **review in `RecipeForm` first**. Do not write the catalog or recipe until the user hits Save.
- LLM runtime: **optional Ollama sidecar** (compose profile). `meal-planner:prod` stays slim.
- Content language: **mostly Polish**. Keep extracted text in the source language; do not translate.

## Non-goals

- URL scraping / server-side `GET` of user URLs (iteration 2)
- Cloud LLM fallback
- Auto-save, fuzzy ingredient merge UI, recipe translation, auth, OpenAPI, GPU compose
- SQLite schema changes

## Architecture

```
RecipeImport  --POST /api/recipes/parse-->  ingest.service.parse_recipe
                                                 |
                    html.strip / JSON-LD         catalog remap         Ollama /api/chat
                    (stdlib)                     (case-insensitive)    qwen2.5:1.5b
                                                 |
                                           ParsedRecipe draft (no DB writes)
                                                 |
                         navigate /recipes/new { state: draft }
                                                 |
                                           RecipeForm review → POST /api/recipes
```

Package: `meal_planner_app/ingest/` (`html_extract.py`, `schema.py`, `llm_client.py`, `prompts.py`, `service.py`). Flask and CRUD stay out of HTML/LLM guts. CRUD is a **read** of catalog names for remapping only.

## API

`POST /api/recipes/parse`

Request: `{ "text": "...", "source_url": "https://..." }`  
`text` required, max 200 KiB. `source_url` optional http(s); copied to the draft; never invented by the model.

Success 200: create-recipe-shaped JSON plus `meta.parser` (`jsonld+llm` | `llm` | `jsonld`) and `meta.model`.

Errors: 400 empty/oversize/bad URL; 422 no usable name+instructions; 503 LLM unset/unreachable; 504 timeout.

Does **not** insert ingredients or recipes.

## Orchestration

1. Strip HTML (`script`/`style`/`nav`/`footer`/`head`). Extract schema.org Recipe JSON-LD when present.
2. If JSON-LD has name, instructions, and ingredient lines: LLM **only** splits lines into `{name, quantity, unit}`.
3. Else one LLM call on stripped text (capped at 8 000 characters).
4. Remap ingredient names onto the catalog with case-insensitive equality (`cebula` → `Cebula`). No fuzzy match.
5. Canonicalize g/kg/ml/l family units; leave `szt` / `op` / `ząbek`. Location left empty.

Default model: `qwen2.5:1.5b`. Env: `LLM_BASE_URL`, `LLM_MODEL`, `LLM_TIMEOUT_SECONDS`.

## Key decisions

| ID | Decision | Why |
|---|---|---|
| KD-1 | Preview API, save via existing create | Tiny models err; catalog hygiene; reuses `RecipeForm` |
| KD-2 | Optional Ollama sidecar, not in prod image | 1B GGUF would dominate the slim Python image |
| KD-3 | JSON-LD + strip first, LLM for leftovers | Makes 1.5B viable on Polish food blogs |
| KD-4 | Default `qwen2.5:1.5b`, Polish kept as-is | Smaller English-first 1B models are weak on PL JSON |
| KD-5 | `source_url` is a user field | LLM must not invent attribution |
| KD-6 | Case-insensitive name remap only | `find_by_name` is case-sensitive |
| KD-7 | No schema migration | Recipe/ingredient models already have the fields |
| KD-8 | Fetch is a later module | Parse contract stays URL-agnostic |

## PR Plan

1. HTML/JSON-LD ingest + tests
2. Parse service + `POST /api/recipes/parse` + compose
3. Import UI + RecipeForm draft seeding + i18n + Playwright intercept
4. Spec, README, `.ai/next_step.md`

## Iteration 2 (implemented)

`meal_planner_app/ingest/fetch.py` GETs a public `http(s)` URL (15s timeout, 200 KiB cap, text/html|plain|xml only). Private, loopback, link-local, and metadata IPs are denied (SSRF), including after redirects.

- `POST /api/recipes/fetch` `{url}` → `{text, source_url, content_type}` (no LLM, no DB).
- `POST /api/recipes/parse` with `source_url` and empty `text` fetches, then parses.
- Import UI: **Fetch page** fills the textarea; **Parse recipe** works with URL only.

Still review in `RecipeForm` before Save.
