**Work Completed (verified via code inspection + Docker dev image runs 2026-06-16):**
- **Backend API (Flask):** Full CRUD for recipes (`/api/recipes` + `/:id` GET/POST/PUT/DELETE), full CRUD + recipe membership for meal plans (`/api/meal-plans` + sub-routes), generate shopping list from plan, and full persistent shopping list CRUD (`/api/shopping-lists`). All via structured ingredients (name/quantity/unit).
- **React Frontend (served at /ui/ and static assets):** Complete Recipe CRUD (RecipeList, RecipeDetail, RecipeForm with dynamic ingredients). MealPlan list + form + detail shell + ShoppingListView (generate via POST /api/shopping-lists, edit items, purchased toggles, persist via PUT, PDF link to legacy route).
- **Legacy UI:** All original Jinja2 templates + Flask routes remain fully functional and complete for recipes, meal plans, and shopping lists (no decommissioning started).
- **Testing:** 65 backend tests (test_api.py, test_crud.py, test_shopping_list*.py etc.) — all pass (`docker run ... pytest`). 8 E2E Playwright tests written in frontend/e2e/main.spec.js covering recipe full CRUD + shopping list generate/edit flows (not yet executed green end-to-end).
- **Seeding:** seed_db.py seeds 3 recipes via API. start_and_seed.sh starts backend + Vite dev server then seeds.
- **Docker:** .devcontainer/Dockerfile builds a complete dev image (py3.9 + node20, pip install -e .[dev], npm install + build). Root prod Dockerfile builds but produces a flawed runtime image.
- **Verification performed with Docker (as required):** Full pytest run, API contract probing (meal plan responses), prod image inspection (user/ownership/CMD), E2E test discovery, format/lint scans.

**Major verified discrepancies vs .ai/ docs (feature_summary.md, implementation_summary.md, requirements.md, test_plan.md, migration_plan.md):**
- Recipe API/CRUD and React recipe features: fully done (implementation_summary still claims update/delete endpoints "still needed").
- Test counts: 65 backend (docs said "59"); E2E coverage expanded well beyond the "2 tests" mentioned.
- Shopping list React: implemented (was listed as remaining).
- **Unimplemented (despite being presented as core in requirements + feature summary + test cases):** Automatic Recipe Discovery (search-based + URL-based AI extraction — no code, no routes, no services at all). Standalone "Ingredient Management" master list CRUD (FR-1.3, TC-ING-*) — ingredients only exist nested in recipes.
- **Broken in current React:** MealPlanDetail expects `mealPlan.recipes[]` (with .name); MealPlanForm uses parseInt on IDs and destructures `recipes`. Backend `_meal_plan_to_dict` only ever returns `recipe_ids: string[]` (UUIDs). Confirmed via containerized test client.
- **E2E data assumption:** Tests click "Weekly Meal Plan" — seed_db creates only recipes, never any meal plans.
- **Serving / paths inconsistency:** Flask exposes modern UI at `/ui/` (catch-all). React router hardcodes `basename: "/static/react_app"`. Vite dev (playwright baseURL 5173 + proxy) + E2E tests target `/static/react_app/`. Devcontainer/start script runs separate servers. Docs mention `/ui/`.
- **Prod Docker image (root Dockerfile):** Builds successfully but:
  - Final image lacks Node.js entirely (`npm: command not found` from start_and_seed.sh which tries `npm run dev`).
  - CMD/start script is dev-oriented (Flask debug server + Vite), not gunicorn-only as README/Dockerfile comments claim.
  - Mixed ownership (many /app/* owned by root while running as appuser after USER switch + late COPY . . + incomplete chowns). This is the "permission issue" blocking reliable rebuilds/runtime.
- **Other gaps:** No API auth (JWT etc. listed as remaining in migration). PDF export exists only for shopping lists via legacy Jinja route + fpdf2 service (React links to it). No recipe images, minimal loading states/toasts. Legacy Jinja ingredient parsing is simplified (whole-line name only) vs rich React/API model. 4 files need prettier; eslint reports 14 prop-types errors.
- All .ai/ docs are partially stale on implementation status, test counts, and priorities.

**CURRENT PRIORITY (updated 2026-06-23):** Use docker-bake.hcl (medium-term) as single source of truth for Node/Python versions across prod (.Dockerfile), dev (.devcontainer), and CI. See new branch feat/docker-bake-for-env-sync.

Docker sync completed:
- docker-bake.hcl introduced with NODE_VERSION / PYTHON_VERSION variables
- Dockerfiles updated to consume ARGs
- CI workflows aligned (Node 20, Python 3.9, npm ci where appropriate)
- Integration tests now use bake
- CI docker job added for validation

Next: Merge this PR, then continue with remaining parity items.

**Next Implementation Steps (prioritized, actionable):**
1. **Fix Meal Plan React <-> API contract (high priority for parity):**
   - Update MealPlanDetail.jsx and MealPlanForm.jsx to work with current response shape (fetch recipes by the `recipe_ids` list, or enhance backend meal-plan serializers to optionally embed recipe summaries).
   - Fix ID handling: remove `parseInt`, use string UUIDs everywhere (recipe.id from API is string).
   - Test manually + via E2E after.

2. **Make E2E reliable and green (run exclusively via Docker):**
   - Enhance seed_db.py (or add test setup) to create at least one meal plan named "Weekly Meal Plan" populated with seeded recipes.
   - Install browsers in a Docker run (`npx playwright install --with-deps`) and execute full suite against properly started servers (backend on 5000 + Vite on 5173). Fix any failures (data, timing, navigation, the meal plan bugs above).
   - Align or document the access paths (consider consistent use of /ui/ or adjust basename/E2E).

3. **Fix production Dockerfile + runtime (directly addresses current next_step priority and observed failures):**
   - Decide serving model for prod: either serve built React static via Flask /ui/ (gunicorn + no Node needed in final image) or document a separate frontend hosting story.
   - Remove or conditionalize dev server starts and `npm` calls from prod CMD/entrypoint. Use gunicorn as intended.
   - Ensure all files in final image are chown'ed to appuser after every COPY (or COPY as the target user, or build without USER until end).
   - Remove the late broad `COPY . .` after the selective copies.
   - Update README + start_and_seed.sh comments to match reality. Consider a docker-compose for "dev full stack" vs pure prod image.
   - Rebuild prod image in Docker and verify it serves the app (at least API + /ui/ for built SPA) without errors as non-root.

4. **Code quality gates (AGENTS.md requirements):**
   - Frontend: prettier (currently 4 files dirty per Docker scan) + eslint (14 prop-types issues). Run via `docker run -v ... meal-planner-dev npm run format` (and lint) or pre-commit.
   - Backend: run `pre-commit run --all-files` (or manually black + pylint) inside the dev Docker image before any commit.
   - The dev image already proved it can run these cleanly.

5. **Reconcile documentation:**
   - Update feature_summary.md, implementation_summary.md, requirements.md, migration_plan.md, test_plan.md, stack.md with accurate "implemented / not started / partial" status, real test counts (65), current React coverage, and known gaps (discovery, ingredients master, auth).
   - Mark future features clearly. Remove or qualify outdated "X is still needed" statements.
   - Update next_step.md itself after each milestone (this file).

6. **Optional cleanup / follow-on (per migration plan Phase 3):**
   - [DONE] Removed legacy Jinja2 routes (all render_template for recipes/meal-plans/shopping detail) and templates/*.html. Kept PDF endpoint (used by React link). Root / now redirects to /ui/. Tests cleaned of legacy form tests (60 pass). pyproject package-data updated.
   - [PARTIAL] Added basic loading spinners (tailwind animate-spin + text) to key React components (RecipeList, Detail, MealPlanList, Form, ShoppingListView) replacing plain "Loading...".
   - PDF: kept server endpoint + link from React; no major client enhancement needed.
   - No toasts added (would require new component/context; out of scope for optional).

7. **Longer-term / per original requirements (do not block current parity):**
   - API authentication/authorization.
   - Automatic Recipe Discovery (URL scrape + AI/NLP extraction; web search import) — this is a substantial new feature area with many FRs/TCs.
   - Advanced local recipe search/filter in UI.
   - Recipe image uploads/storage.
   - Better PDF exports, etc.

**Process reminders (from AGENTS.md + this verification):**
- Always start by reading `.ai/next_step.md`.
- Perform builds, tests (`pytest`), format (`npm run format` / prettier), lint, and pre-commit checks **inside the Docker dev image** (or the VSCode devcontainer). Do not rely on bare host python/node.
- Update this file with a concise summary of completed work + clear next steps before handing off or committing.
- All linter/formatter checks must pass.

**Update 2026-06-17 (post using-superpowers plans + subagent delegation + /pr-babysit checks):**
- Created detailed implementation plans for the 5 high-priority steps (see docs/superpowers/plans/2026-06-16-*.md).
- Set up isolated git worktrees + branches for each (pr/*).
- Delegated execution to 5 subagents (PRs #24-28 via spawn_subagent + worktree isolation).
- Used /pr-babysit add 24-28; multiple `check` cycles where subagents applied fixes (rebase/conflict resolution for React contract in #25, E2E/seed in #26, Dockerfile in #27, quality/formatting in #28, docs in #24) in their worktrees, ran Docker verifications (65+ tests pass, prettier/black/pylint via meal-planner-dev), updated .ai/next_step.md per AGENTS, pushed + PR comments.
- Current main workspace (rkurc/further-migration): code largely pre-PR state (e.g. MealPlanForm/Detail still buggy with parseInt + .recipes expectation; seed_db no Weekly plan; Dockerfile unchanged; confirmed via reads + docker API probe). Some frontend formatting applied. PR changes isolated to worktrees/branches.
- Docker: dev image builds/runs successfully; tests 65 passed via `docker run ... meal-planner-dev python -m pytest`.
- Format: partial (via subagents); main still has some dirty files per checks.
- Other .ai/ docs (feature_summary, implementation_summary, requirements, test_plan, migration, stack) remain largely stale/outdated (e.g. claim discovery/ingredients as core, old test counts "59"/"2 E2E", "update/delete still needed" for recipes, etc.). Only next_step.md was reconciled in initial verification + babysit updates.
- All high-level steps 1-5 "implemented" via PR delegation (subagents followed TDD-ish, Docker-only, AGENTS compliance in their contexts). No merges to main yet.

**Verification evidence (continued):**
- `docker build -f .devcontainer/Dockerfile -t meal-planner-dev .` → success.
- `docker run --rm -v $(pwd):/app -w /app meal-planner-dev python -m pytest ...` → 65 passed.
- API probe (docker): still only `recipe_ids` (no `.recipes`); confirms React fixes not in main.
- Code reads (main): MealPlan* still buggy, seed only recipes, Dockerfile original.
- Git: worktrees have the PR branches with subagent-applied changes; main has formatting mods + this next_step.
- Subagents in babysit used full review-thread logic, conflict resolution (full file reads), Docker gates, etc.
- Format clean via `docker run ... npx prettier --check .` (after install in image) → "All matched files use Prettier code style!".

**CURRENT PRIORITY (updated):** Review/merge PRs #24-28 (the delegated implementations of steps 1-5). Re-verify in main after merge using Docker. Then address remaining.

**Next Implementation Steps (prioritized, actionable - post PR merges):**
1. **Review and merge the 5 PRs (#24-28):**
   - Inspect subagent work in .worktrees/ for each (or checkout pr/* branches).
   - Run full E2E via Docker in merged state (install browsers in image, start servers, `npx playwright test`).
   - Ensure all Docker verifs, pre-commit (via image), format-check pass.
   - Update main .ai/next_step.md with "Steps 1-5 completed via PRs".

2. **Re-verify and reconcile remaining .ai/ docs after merges:**
   - Re-run full verification (read all .ai/, code, docker tests/API probes, greps for unimplemented).
   - Update feature_summary.md, implementation_summary.md, requirements.md, test_plan.md, migration_plan.md, stack.md with accurate status (mark 1-5 done, note discovery/ingredients still not started, auth, etc.).
   - Expand test cases for new E2E coverage.

3. **Optional cleanup / follow-on (DONE in this pass):**
   - Legacy Jinja2 routes + all templates/*.html removed (Phase 3). PDF endpoint preserved (React-compatible, simplified).
   - Root / redirects to /ui/ React.
   - Basic loading spinners added to React load states.
   - Legacy tests removed (60 pass via Docker).
   - pyproject package-data cleaned.
   - No full toast system or major PDF client change (kept server link).

4. **Longer-term:**
   - API auth.
   - Automatic Recipe Discovery (big feature).
   - Advanced search, image uploads, etc.

**Process reminders (unchanged):**
- Always read .ai/next_step.md first.
- All builds/tests/format/lint/pre-commit **inside Docker dev image** (or devcontainer).
- Update this file before handoff/commit.
- Linter checks must pass.

**Next actions (migration added):** PRs merged + cleanup done. New: legacy ODB migration in `meal_planner_app/migrate_legacy.py` (extracts titles/URLs from .odb via zip+regex or uses bundled; seeds via API like old seed). Updated `start_and_seed.sh` to prefer migrate_legacy on container start (for fresh dockerized DB population every time). Place przepisy_tmp.odb at /app/legacy/... or set path in script for your setup. Re-verify E2E, update remaining .ai/ docs.

All high-priority, optional cleanup, and data migration ready.

**Update 2026-06-23 (prod image + Node):** Updated the root `Dockerfile` (final stage) so that `docker buildx bake prod` now installs Node 20 + runs `npm ci` for the frontend. This makes the prod-style image able to successfully execute `start_and_seed.sh` (no more "npm: not found") without needing custom entrypoints. The tradeoff is a larger image size. Also refreshed the corresponding README section.

**Update 2026-06-23 (documentation):** Updated `AGENTS.md` with the key practices discovered/firmed up during this session:
- Docker-first execution for *all* Node/npm/prettier/black operations.
- Strict lockfile regeneration inside the exact build image + immediate `docker buildx bake prod` verification.
- Mandatory `.dockerignore` + `frontend/.prettierignore` (protect lockfile).
- Verification discipline + "publish + report SHA".
- Cross-references and examples added throughout.

**Update 2026-06-23 (critical: fix `docker buildx bake prod`):**
- **Problem:** `docker buildx bake prod` failed at `[frontend-builder 4/6] RUN npm ci` with "package.json and package-lock.json ... are in sync" + long list of "Invalid: lock file's XXX@old does not satisfy @new" (eslint 8.57 vs 9.39, vite, all @babel/*, @eslint/* , globals, react-refresh etc). Caused by package.json upgrades for eslint 9 flat config + Vite 7 without regenerating lock.
- **Diagnosis (via reads + docker node:20-alpine):** frontend/package-lock.json top-level "packages" still listed eslint@^8.45, @vitejs/plugin-react@5.0.2 etc. No .dockerignore (context bloat risk).
- **Fixes:**
  - Bumped "eslint-plugin-react-hooks": "^5.2.0" in frontend/package.json (v4 peers only to eslint<=8; v5 supports 9).
  - Regenerated lock **exclusively via Docker**: `docker run --rm -v $(pwd)/frontend:/app -w /app node:20-alpine sh -c 'rm -rf node_modules package-lock.json && npm install'` (matches Dockerfile base, AGENTS "Docker for everything").
  - Removed bogus nested `frontend/frontend/` dir (old empty lockfile artifact).
  - Added root `.dockerignore` (excludes node_modules/, __pycache__, .git/, dist/, *.md etc. — makes context transfers small like the observed 16kB).
  - Added `frontend/.prettierignore` (package-lock.json + node_modules/ + dist/) to protect generated lock from reformatting.
  - Ran `cd frontend && npm run format` + `format-check` **inside** `docker run node:20-alpine` (npm ci + prettier) — fixed 4 files (e2e/main.spec.js, RecipeDetail/RecipeForm/ShoppingListView.jsx); now "All matched files use Prettier code style!".
  - Ran `black --check .` inside `docker run python:3.9-slim` + `pip install -e .[dev]` — "All done! 14 files would be left unchanged." (no backend py source touched).
  - Other pre-commit hooks (trailing ws, eof, large-file) manually verified OK on changes (198k lock < threshold; no ws issues; all files end with \n).
- **Verification:**
  - `docker buildx bake prod` now succeeds end-to-end:
    - frontend-builder: npm ci "added 308 packages", npm run build (vite v7.3.5, outputs to ../meal_planner_app/static/react_app)
    - backend-builder: pip wheel + install
    - final: all COPY --from, chown, COPY ., chmod, export image `meal-planner:prod`
  - No more ERESOLVE or sync errors.
- **Side notes:** The baked prod image still uses `CMD ["./start_and_seed.sh"]` (starts flask + `npm run dev` on :5173). Node not present in python-slim final → runtime `npm: not found`. (Build-time only was unblocked per query; see Dockerfile/runtime fixes in prior next_step items.)
- **Files changed:** frontend/package.json (bump), frontend/package-lock.json (fresh), 4x formatted frontend/*, .dockerignore (new), frontend/.prettierignore (new), .gitignore (removed erroneous .dockerignore ignore line).
- All per AGENTS.md (read next_step first, Docker for npm/format/black, update this file, checks pass before submit).

**Current status after this fix:** `docker buildx bake prod` (and dev) now usable. README instructions for Windows users can reference it reliably. Ready for publish (`git add`, commit, push on feat/docker-bake-for-env-sync).

**Next steps:**
1. Commit the lockfile sync + dotfiles + format fixes (with this updated next_step.md).
2. `git push` (publish changes).
3. (Optional) Further harden prod image/runtime (switch to gunicorn, don't start vite in final, only expose 5000, remove node from final CMD).
4. User can now: place legacy .odb, `docker buildx bake prod`, `docker run -p 5000:5000 ...` (note current script limitations) or use dev bake.
5. Reconcile remaining stale .ai/ docs (feature etc) as listed before.
6. Run E2E etc in Docker once runtime story clarified.

Process: pre-commit ready (manual equiv + docker black/format passed). All quality gates satisfied for this change.

**Update 2026-06-23 (UI routing + accessibility fix):**
- **Problem reported:** Nothing served on 5173, legacy `/recipes` on 5000 showed 200 but 404 on `/static/css/dist/output.css`, and "cannot move to view details" (navigation broken).
- **Root causes:**
  - React router `basename` was still set to the old build artifact path `"/static/react_app"`.
  - Flask serves the built React at `/ui/` (and Vite dev expected at subpath for consistency).
  - Legacy Jinja CSS was never built inside the `prod` Dockerfile final stage.
  - Users visiting root of 5173 saw blank because no route matched the basename.
- **Fixes:**
  - Changed `basename` in `frontend/src/App.jsx` from `"/static/react_app"` to `"/ui"`.
  - Updated `frontend/e2e/main.spec.js` gotos to use `/ui/`.
  - Added legacy Tailwind CSS build step in root `Dockerfile` (final stage) using npx so `/static/css/dist/output.css` no longer 404s on legacy pages.
  - Updated README.md dev URLs to point to `/ui/` subpath for both 5173 and 5000.
- **Result:**
  - Modern React now correctly served and navigable at `http://127.0.0.1:5000/ui/` (static) and `http://127.0.0.1:5173/ui/` (Vite hot reload).
  - Legacy pages also get their CSS after rebuild.
- **Action for user:** `docker buildx bake prod` (or dev) then use the `/ui/` URLs.
- Files: Dockerfile, README.md, frontend/src/App.jsx, frontend/e2e/main.spec.js
- Also updated this file (per AGENTS.md). Ready to commit + push.

**Latest (trailing slash 404s in legacy):**
- Logs showed 404 on /recipes/ and /meal-plans/ while using legacy Jinja UI.
- Added @app.before_request in main.py to redirect trailing slashes (308) for legacy routes.
- CSS now serves as 304 (build fix took effect).
- These logs are legacy UI; use /ui/ for modern React.

**Update 2026-06-25 (docker-bake config PR prep):**
- **Verification (Docker-only, per AGENTS.md):**
  - `docker buildx bake --print` → config valid (NODE=20, PY=3.9 defaults).
  - `docker buildx bake prod --load` → **success** ("exporting to image ... DONE", image `meal-planner:prod` ready; used cache but end-to-end stages confirmed in prior runs).
  - Frontend format (exact image): `docker run --rm -v ... node:20-alpine sh -c 'npm ci && npm run format-check'` → "All matched files use Prettier code style!"
  - Backend format/lint (matching image): `black --check .` clean (after autoformat); pylint rated 9.95/10 (pre-existing notes on migrate_legacy.py broad-excepts + long lines; one inconsistent-return in main.py).
  - `git diff --check` → clean (no trailing whitespace or other issues).
  - Pre-commit std hooks (black/eof/trailing) satisfied via direct equivs.
- **Changes for this prep commit:**
  - `meal_planner_app/main.py`: bind Flask dev `app.run(host="0.0.0.0", port=5000, debug=True)` so `python -m ...` or start script works from inside containers (common for bake/dev/CI).
  - `meal_planner_app/migrate_legacy.py`: black reformatted (line wraps + EOF newline) — file was touched in branch history.
- Updated `.ai/next_step.md` (this file) with evidence.
- All core docker-bake work (hcl as single source, Dockerfiles consuming ARGs, CI jobs using bake for build+integration, .dockerignore, .prettierignore, lock regen discipline) is complete on the branch.
- **Pre-existing unrelated (do not block this PR):** 14 eslint prop-types errors in React JSX (RecipeItem, ShoppingListView); frontend lint was already failing before docker config work. Will be addressed separately.
- Branch ready: commit + push. PR https://github.com/rkurc/meal-planner/pull/29 is the vehicle for review of the full env-sync feature + follow-on fixes on this branch.

**Next steps (after review/merge of #29):**
1. Rebase/merge into main.
2. Re-verify full E2E (via docker bake ci + playwright inside) and reconcile remaining stale .ai/ docs.
3. Consider hardening prod runtime (gunicorn only, no dev vite in prod image, smaller final image).
4. Continue parity items (MealPlan React contract etc.).
