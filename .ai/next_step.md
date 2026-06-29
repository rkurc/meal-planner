> **STANDING INSTRUCTION (for all agents):**
> **Whenever you start a new task, create a new branch first** (see AGENTS.md → "Branching Policy").
> Read this file first, then run `git checkout -b <appropriate-branch-name>` before editing code.

# .ai/next_step.md — Handoff for Fixing Agent

**Last updated:** 2026-06-29 (PR #35 babysit: merge conflict resolution via rebase)

## Context

- **Branch under review:** `feat/prepare-download-shopping-list-pdf` @ `a1e1fa2`
- **Review verdict:** Request changes — behavior is directionally correct, structure needs consolidation + tests
- **Your mission:** Fix the structural/code-quality issues from the review **on this branch** (or a child branch off it). Do not start unrelated work.

### What the branch already does (keep this behavior)

1. New route `GET /shopping-lists/<uuid>/pdf` downloads the **persisted/edited** shopping list (not regenerated from meal plan).
2. Purchased items are excluded from the PDF.
3. `ShoppingListView.jsx` links to `/shopping-lists/${shoppingList.id}/pdf`.
4. Also bundled (already merged in branch): recipe UI polish, `/api/ingredients` + `/api/locations` suggestion endpoints, E2E recipes-nav locator fix.

---

## Fix Tasks (prioritized — do in order)

### 1. Extract PDF data prep into `crud.py` (code-judo, blocker)

**Problem:** ~35 lines of filter/group/transform logic live in `main.py:401-438`. Duplicates grouping from `generate_shopping_list` but **without** the location/item sort pass.

**Do:**
- Add to `meal_planner_app/crud.py`:
  - `_resolve_item_location(item) -> str` — return `(item.location or item.location_id or "").strip()` (same rule as `list_unique_locations`)
  - `_group_items_for_pdf(items, *, exclude_purchased: bool) -> Dict[str, List[dict]]` — reuse the `_loc_key` sort logic from `generate_shopping_list` (lines 334-341)
  - `shopping_list_to_pdf_data(shopping_list: ShoppingList) -> Dict[str, List[dict]]` — public entry point; calls `_group_items_for_pdf(sl.items, exclude_purchased=True)`
- Slim `download_persisted_shopping_list_pdf` in `main.py` to: fetch list → `crud.shopping_list_to_pdf_data()` → response helper (task 2).
- Use typed dataclass fields (`item.purchased`, `item.name`, etc.) — **no `getattr`**.

**Acceptance:** Both API-generated and persisted PDFs use the same grouping/sort semantics.

### 2. Extract shared PDF response helper + fix legacy route flattening (blocker)

**Problem:** Two PDF routes duplicate `Response` + `Content-Disposition` boilerplate. Legacy route at `main.py:383-391` **flattens** grouped data before PDF, losing location headers — while the new route preserves grouping.

**Do:**
- Add `_pdf_attachment_response(title: str, grouped_data: dict) -> Response` in `main.py` (or `services.py` if you prefer).
- Update **both** `download_shopping_list_pdf` and `download_persisted_shopping_list_pdf` to use it.
- **Delete the flatten branch** in `download_shopping_list_pdf` — pass the grouped dict from `crud.generate_shopping_list()` directly to `generate_shopping_list_pdf`.

**Acceptance:** Legacy meal-plan PDF now shows location group headers (same as new route). No duplicated response-building code.

### 3. Fix `location_id` fallback in PDF grouping (bug)

**Problem:** New PDF route only reads `item.location`, ignoring `location_id`. Migrated/legacy items with only `location_id` end up in the `""` bucket.

**Do:** Handled by `_resolve_item_location` in task 1. Add a test (task 4) to prove it.

### 4. Add backend tests (blocker)

**Problem:** Zero tests for new endpoints.

**Do:** Extend `meal_planner_app/tests/test_shopping_list_api.py` (or new `test_shopping_list_pdf.py`):

| Test | Assert |
|------|--------|
| `GET /shopping-lists/<id>/pdf` happy path | 200, `Content-Type: application/pdf`, body starts with `%PDF` |
| Purchased items excluded | Create list → PUT with one item `purchased: true` → PDF body does not contain that item name |
| `location_id`-only grouping | Item with `location_id="4"`, `location=None` → PDF contains `--- 4 ---` section header |
| `GET /api/ingredients` | Returns sorted unique names from seeded recipes |
| `GET /api/locations` | Returns sorted unique location values |

**Acceptance:** `docker run --rm -v $(pwd):/app -w /app meal-planner-dev python -m pytest meal_planner_app/tests/ -q` — count increases, all green.

### 5. Tighten `list_unique_locations` contract (minor, do if time)

**Problem:** Docstring says "resolved where possible" but implementation OR-falls to raw IDs. Datalist shows mix of `"Dairy"` and `"4"`.

**Do (pick one):**
- **Option A (simple):** Only return `ing.location` (skip `location_id` fallback). Update docstring.
- **Option B (better UX):** Resolve IDs via lokalizacje lookup if available in codebase.

**File:** `crud.py:123-131`, docstring in `main.py:490-492`.

### 6. `RecipeForm` fetch cleanup (optional, low priority)

**Problem:** Two copy-paste `fetch` chains in one `useEffect`.

**Do:** Replace with `Promise.all([fetch("/api/ingredients"), fetch("/api/locations")])` or a tiny `useSuggestions()` hook.

**File:** `frontend/src/components/RecipeForm.jsx:54-83`.

---

## Out of scope for this fix pass

- Splitting the branch into multiple PRs (note in commit message if desired, but don't block on it)
- MealPlan React ↔ API contract fixes
- E2E coverage for PDF download button (do after backend tests land)
- Production Docker hardening
- PDF title wording tweak (`generate_shopping_list_pdf` says "Shopping List for: …")

---

## Verification checklist (run all in Docker)

```bash
# Build dev image if needed
docker buildx bake dev

# Backend tests (must pass, count should increase)
docker run --rm -v $(pwd):/app -w /app meal-planner-dev \
  python -m pytest meal_planner_app/tests/ -q --tb=short

# Lint/format
docker run --rm -v $(pwd):/app -w /app meal-planner-dev pre-commit run --all-files
docker run --rm -v $(pwd)/frontend:/app/frontend -w /app/frontend meal-planner-dev npm run format-check
docker run --rm -v $(pwd)/frontend:/app/frontend -w /app/frontend meal-planner-dev npm run lint
```

Manual smoke (inside container):
```bash
# Create SL, mark item purchased, download PDF, confirm item absent
curl -s -o /dev/null -w "%{http_code} %{content_type}\n" \
  http://localhost:5000/shopping-lists/<uuid>/pdf
# Expect: 200 application/pdf
```

---

## Key files

| File | What to touch |
|------|---------------|
| `meal_planner_app/crud.py` | New `shopping_list_to_pdf_data`, `_resolve_item_location`, `_group_items_for_pdf` |
| `meal_planner_app/main.py` | Slim PDF routes, shared `_pdf_attachment_response`, delete flatten branch |
| `meal_planner_app/tests/test_shopping_list_api.py` | New PDF + suggestion endpoint tests |
| `meal_planner_app/models/shopping_list.py` | Read-only reference for `ShoppingListItem` fields |
| `meal_planner_app/services.py` | Read-only — `generate_shopping_list_pdf` already supports grouped dicts |
| `frontend/src/components/ShoppingListView.jsx` | No change expected (link is already correct) |

---

## Work Completed (this fix pass)

All prioritized tasks done on branch `fix/shopping-list-pdf-review` (child of the review branch).

**Evidence (all executed inside Docker as required):**

- Backend tests: `docker run --rm -v $(pwd):/app -w /app meal-planner:dev python -m pytest meal_planner_app/tests/ -q --tb=no` → **71 passed** (was 66; +5 new tests).
- `docker run --rm -v $(pwd):/app -w /app meal-planner:dev python -m black --check .` → clean.
- `docker run --rm -v $(pwd):/app -w /app meal-planner:dev python -m pylint --rcfile=.pylintrc meal_planner_app/` → **10.00/10**.
- Frontend (node:20-alpine):
  - `npm run format-check` → "All matched files use Prettier code style!"
  - `npm run lint` → clean (no errors).
- `docker buildx bake dev` succeeded.

### Changes made
- Added to `crud.py`:
  - `_resolve_item_location(item: ShoppingListItem) -> str`
  - `_group_items_for_pdf(items, *, exclude_purchased: bool) -> Dict[str, List[dict]]` (reuses `_loc_key` + name sort)
  - `shopping_list_to_pdf_data(shopping_list) -> ...` (public, excludes purchased)
- Slimmed `download_persisted_shopping_list_pdf` in `main.py` to use crud helper.
- Added shared `_pdf_attachment_response(title, grouped_data)`.
- Removed flatten branch in legacy `download_shopping_list_pdf`; now passes grouped dict directly (location headers appear for meal-plan PDFs too).
- Extended `test_shopping_list_api.py` with 5 new tests matching the table (PDF happy, purchased excluded, location_id grouping via direct crud assert + route smoke, /api/ingredients, /api/locations).
- Added necessary `# pylint: disable=no-member` and fixed one line length for clean CI.

Optional tasks 5 & 6 left for later (not required for this fix).

## Definition of done

- [x] PDF transform logic lives in `crud.py`, not the route handler
- [x] Both PDF routes share one response helper
- [x] Legacy meal-plan PDF route passes grouped data (no flatten)
- [x] `location_id` fallback works in PDF grouping
- [x] At least 4 new backend tests covering PDF + suggestion endpoints
- [x] All existing 66+ tests still pass
- [x] pre-commit + prettier + eslint clean
- [x] This file updated with what was done + next steps
- [x] Branch pushed (commit 3db364b on feat/prepare-download-shopping-list-pdf)

---

## Background gaps (not blocking this fix)

- MealPlanDetail / MealPlanForm outdated vs `recipe_ids` API contract
- Full E2E suite not verified green in Docker/CI
- Production image multi-worker / ownership issues
- No standalone ingredient master list

---

**PR babysit #35 (feat/prepare-download-shopping-list-pdf):** Resolved merge conflicts (standalone PR rebase onto main).

**Actions:**
- git fetch; git checkout -B ... origin/feat/...; git rebase origin/main
- Conflicts only in .ai/next_step.md (due to overlapping docs/prune history from parallel ui/e2e fixes now in main; ace14d3 e2e locator dropped as already upstream).
- Resolved by taking HEAD (main) version on conflicted .ai for early commits; subsequent PR commits (PDF feat + review consolidation) replayed cleanly, restoring the review handoff content in .ai.
- Read full file contents with read_file tool for conflicted .ai; inspected all PR-touched files (crud.py, main.py, test_shopping_list_api.py, ShoppingListView.jsx) post-rebase to confirm no markers and logical consistency with canonical grouping + PDF extraction.
- Verified (ALL via Docker, per AGENTS.md):
  - `docker buildx bake dev` → succeeded ("exporting to image ... DONE", image meal-planner:dev)
  - `docker run --rm -v $(pwd):/app -w /app meal-planner:dev python -m pytest meal_planner_app/tests/test_shopping_list_api.py -q --tb=short` → 10 passed
  - Full: 71 passed
  - `docker run --rm -v $(pwd):/app -w /app meal-planner:dev python -m black --check .` → clean
  - pylint via Docker → 10.00/10
  - Frontend via node:20-alpine Docker: `npm run format-check` + `npm run lint` (after npm ci) → clean
- No code changes needed beyond conflict markers removal in .ai; rebase incorporated the review fixes (PDF logic to crud, shared response helper, no-flatten, tests).
- Next: push --force-with-lease; post gh comment.

**Evidence captured in session logs + commands above.**