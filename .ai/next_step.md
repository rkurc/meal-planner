> **STANDING INSTRUCTION (for all agents):**  
> **Whenever you start a new task, create a new branch first** (see AGENTS.md → "Branching Policy").  
> Read this file first, then run `git checkout -b <appropriate-branch-name>` before editing code.

# .ai/next_step.md — Current State + Next Steps

**Last updated:** 2026-06-28 (pruned history; pushed on chore/prune-ai-next-step-md)

## Current State (what is solid)

- Full recipe + meal-plan + shopping list CRUD via REST API
- React UI at `/ui/`:
  - Clean, simple recipes list (only recipe names, no "(React)", no descriptions, no ingredient counts)
  - Ingredient name + location suggestions via `/api/ingredients` and `/api/locations` (cached in form)
  - Ingredient lists resolve and display human `location` names (not just ids)
- Legacy migration supports relational CSVs (`przepisy.csv` + `skladniki.csv` + `produkty.csv` + units/locations) with clean structured data
- All development enforced through `meal-planner:dev` Docker image
- Backend tests: 66 passing
- Linting/formatting: black + pylint + prettier + eslint enforced

## Known Gaps / Open Items

- MealPlanDetail / MealPlanForm have outdated expectations vs current `_meal_plan_to_dict` (uses `recipe_ids` only)
- E2E tests are written but not consistently green in Docker
- Production Docker image still has issues (multi-worker state problems with in-memory DB, dev-oriented startup, file ownership)
- No standalone ingredient master list
- No recipe discovery / import features
- Many planning docs in `.ai/` and `docs/` are stale

## Next Steps (prioritized, actionable)

1. **Fix Meal Plan React ↔ API contract**
   - Update `MealPlanDetail.jsx` and `MealPlanForm.jsx` to work with `recipe_ids` array (fetch recipes separately or embed summaries on backend).
   - Remove `parseInt` usage and ensure string UUIDs everywhere.
   - Make sure "Weekly Meal Plan" seed data is created reliably.

2. **Make E2E reliable (Docker only)**
   - Ensure seed creates a usable "Weekly Meal Plan".
   - Run full Playwright suite inside the dev image against the proper stack.
   - Fix any remaining timing/locator issues.

3. **Production image & runtime hardening**
   - Decide on serving model (gunicorn + built React at `/ui/` is preferred).
   - Enforce single worker (or move state to a real store if multi-worker needed).
   - Fix file ownership, startup script, and CMD for prod.
   - Verify `docker buildx bake prod` produces a working image.

4. **Follow-ups from recent recipes work (2026-06-28)**
   - Consider richer ingredient suggestions (return common unit/location along with name).
   - After merging `feat/relational-legacy-csv-migration`, test that migrated data shows real location names in lists.
   - Optionally add a simple locations reference (master list) for better UX when picking location in forms.

5. **Documentation hygiene**
   - Prune and update stale `.ai/*.md` and `docs/` files so they match reality.
   - Keep this `next_step.md` short and forward-looking.

6. **Longer term (do not block current work)**
   - Ingredient master data separate from recipes
   - Recipe discovery / AI-assisted import
   - Auth

## Process Rules (non-negotiable)

- **Always** start a new task by reading this file, then immediately creating a fresh branch.
- Run **all** Python, Node, black, pylint, prettier, pytest, and playwright commands inside the `meal-planner:dev` Docker image (or via `docker buildx bake`).
- Update this file with a concise summary + clear next steps **in the same commit** as the code changes.
- Push the branch when done.

---

**Old historical log** has been pruned. Full history of previous work, PR babysitting, and migration iterations remains available in git (`git log --follow .ai/next_step.md`).

**Push:** `chore/prune-ai-next-step-md` pushed with commit `01e4a8d`. Branch published.
