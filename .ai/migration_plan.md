# Migration Plan: From Jinja2 to a Headless API

## 1. Introduction

Strategic plan to finish moving from a hybrid Flask (Jinja + JSON) app to a headless API + React SPA.

**Reconciled 2026-09-02.** Canonical status: `.ai/progress.md`.

**Phase 3 is complete.** React at `/ui/` is the only HTML UI. Leftover work (auth, persistence, OpenAPI) is **not** HTML-migration work.

## 2. Current State vs. Target State

*   **Current State:** Flask serves `/api/*` JSON, PDF downloads, GET redirects from old HTML paths into `/ui/…`, and the built React app at `/ui/`. Jinja templates, form POST handlers, and the Tailwind v3 CSS pipeline are **gone**. React covers recipe/meal-plan/shopping CRUD, recipe search (`GET /api/recipes?q=&ingredient=`), persisted shopping lists, PDF of edited lists, ingredient list, suggestion datalists, and meal-plan recipe counts.
*   **Target State (remaining, not UI migration):** Auth for anything beyond local use. Persistent storage (not in-memory lists). Optional OpenAPI. Optional lean prod image (gunicorn + pre-built `static/react_app` only).

## 3. Phased Migration Strategy

### Phase 1: Solidify the API Foundation *(COMPLETE for current domains; auth/docs/persistence still open)*

*   **Action 1.1: Full API Coverage.** *Done for recipes, meal-plans (including counts), shopping-lists (including standalone + delete), suggestion/summary ingredient endpoints, PDF of persisted lists, recipe search query params.*
*   **Action 1.2: API Authentication.** JWT or similar. *NOT STARTED. Not a Jinja leftover.*
*   **Action 1.3: API Documentation.** OpenAPI/Swagger. *NOT STARTED. Not a Jinja leftover.*
*   **Action 1.4: Search as API.** *Done.* `GET /api/recipes?q=` and `ingredient=` (empty both → list all). No `/api/search`.
*   **Action 1.5: Persistence.** Replace in-memory `*_db` lists. *NOT STARTED. Not a Jinja leftover.*

### Phase 2: Achieve Feature Parity in React *(COMPLETE)*

*   **Action 2.1: Prioritize and Migrate.** Recipes, meal plans, shopping view/edit, standalone lists, ingredient **list**, PDF download, **recipe search**: **done**.
*   **Action 2.2: Consistent UI/UX.** Suggestion datalists + default units.
*   **Action 2.3: Comprehensive Testing.** 83 pytest; 10 E2E covering recipes (including search) + embedded shopping. Gaps: ingredients page, standalone lists, delete, PDF click.

On-the-fly shopping HTML was not rebuilt (React persisted lists are the replacement). Extra shopping E2E (delete/PDF) is useful but was **not** a Phase 3 gate.

**Not in original Jinja, not required for decommission:** discovery, master ingredients, auth.

### Phase 3: Decommission Legacy Components *(COMPLETE)*

**Plan:** `docs/superpowers/plans/2026-09-01-jinja-decommission.md`.

*   **Action 3.0:** Search API + React list (Tasks 1–2). *Done* (`5b2df09`, `a526cd8`).
*   **Action 3.1:** GET redirects from old HTML paths → `/ui/…`; remove form POST handlers (Tasks 3–4). *Done* (`789212c`).
*   **Action 3.2:** Remove `templates/` and Jinja helpers (`parse_ingredients_from_textarea`, `nl2br`). *Done*.
*   **Action 3.3:** Remove Tailwind v3 CSS pipeline (root `package.json` `build:css`, Dockerfile `npx tailwindcss@3`). *Done* (`e273724`).

`GET /` → 302 `/ui/`. Bookmark-friendly legacy GET paths still 302 into the SPA. Both PDF routes kept. Failed meal-plan PDF is 404.

Full Docker verification of the decommission (plan Task 7: bake dev+prod, pytest, Playwright suite) is a **quality gate**, not remaining migration work.

## 4. Key Considerations

*   **API design:** counts vs `recipe_ids`, grouped vs flat shopping generate, standalone lists, search `q`/`ingredient` — already in production shape; document in OpenAPI when added.
*   **Testing:** Playwright against `/ui/` is the regression net. Redirect tests live in `test_api.py`.
*   **Deployment:** Prod image currently still includes Node so `start_and_seed.sh` can run Vite. A leaner target is gunicorn + pre-built `static/react_app` only.

## 5. Recommended next steps (not HTML migration)

1. Task 7 verification of the decommission plan (if not yet run end-to-end).
2. Persistent DB (decommissioning Jinja does not fix “data dies on restart”).
3. Auth + OpenAPI.
4. Dead `IngredientDetail.jsx` cleanup.
5. E2E for shopping delete / standalone / PDF (not a decommission blocker).
6. Discovery and master ingredients are **new features**, not migration work.

See `.ai/next_step.md` for session-level priority.
