# Refactor A — Correctness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Follow superpowers:test-driven-development: no production code without a failing test first. Docker-first: run pytest / node tests via `meal-planner:dev`.

**Goal:** Fix seed isolation, meal-plan PUT/add-recipe honesty, drop non-working purchased checkboxes, stop MealPlanForm from unmounting on submit errors, and proxy PDF paths through Vite.

**Architecture:** No new layers. A1 uses existing `SqliteDao.reset()`. A2 changes HTTP/crud control flow only. A3–A5 are frontend-only. Tasks A1, A2, A3, A4, A5 share no production files and may run in parallel (see `2026-09-10-refactor-parallelism.md`).

**Tech Stack:** Python 3.9, Flask, pytest, React 18, Vite 7, node:test, Docker `meal-planner:dev`.

**Spec:** `docs/superpowers/specs/2026-09-10-codebase-review.md` (A3 = drop checkboxes).

**Do not:** persist purchased; add React Query; touch `migrate_legacy.py`; rename `crud.py`; change ingredient GET shapes.

---

## File map

| File | Role |
|---|---|
| `meal_planner_app/seed_db.py` | `seed_database()` calls `get_dao().reset()` then inserts recipes + Weekly plan |
| `meal_planner_app/tests/test_seed.py` | **New.** Double-seed keeps recipes on Weekly plan; shopping lists cleared |
| `meal_planner_app/crud.py` | Missing recipe on add → `None`; `count` still honored |
| `meal_planner_app/main.py` | PUT applies `recipes` only if key present; POST add-recipe passes `count` |
| `meal_planner_app/tests/test_api.py` | Name-only PUT; add missing recipe 404; add with count |
| `frontend/src/components/ShoppingListView.jsx` | Remove view-mode checkbox + `handleTogglePurchased` |
| `frontend/src/shoppingListView.lock.test.js` | **New.** Source lock: no checkbox / no toggle helper |
| `frontend/src/components/MealPlanForm.jsx` | Split load vs submit error; `t("mealPlans.formHint")` |
| `frontend/src/i18n/leftover-chrome.test.js` | Forbid English MealPlanForm chrome |
| `frontend/vite.config.js` | Proxy `/shopping-lists` and `/meal-plans` to Flask |
| `frontend/src/vite-proxy.test.js` | **New.** Source lock on proxy keys |
| `.ai/next_step.md` | Handoff after each task commit |

Docker:

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/test_seed.py meal_planner_app/tests/test_api.py -q --tb=short

docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  npm run test:unit
```

If `meal-planner:dev` is missing: `docker buildx bake dev`.

---

### Task 1: Seed reset (A1)

**Files:**
- Modify: `meal_planner_app/seed_db.py`
- Create: `meal_planner_app/tests/test_seed.py`
- Do **not** edit `test_crud.py` (keeps A1 ∥ A2). `test_seed_if_empty_is_idempotent` stays as-is: `seed_if_empty` must **not** call `reset()`.

- [ ] **Step 1: Write the failing test**

Create `meal_planner_app/tests/test_seed.py`:

```python
"""E2E/dev seed isolation: seed_database must wipe all aggregates."""

from meal_planner_app import crud
from meal_planner_app.seed_db import RECIPES_TO_SEED, seed_database, seed_if_empty


def _weekly():
    plans = crud.list_meal_plans()
    return next((p for p in plans if p.name == "Weekly Meal Plan"), None)


def test_seed_database_twice_keeps_recipes_on_weekly_plan():
    seed_database()
    crud.create_shopping_list(name="orphan")
    seed_database()

    recipes = crud.list_recipes()
    assert len(recipes) == len(RECIPES_TO_SEED)
    names = {r.name for r in recipes}
    assert names == {r["name"] for r in RECIPES_TO_SEED}

    weekly = _weekly()
    assert weekly is not None
    assert len(weekly.recipes) == len(RECIPES_TO_SEED)
    seeded_ids = {r.recipe_id for r in recipes}
    plan_ids = {e["recipe_id"] for e in weekly.recipes}
    assert plan_ids == seeded_ids

    assert crud.list_shopping_lists() == []
    assert len(crud.list_meal_plans()) == 1


def test_seed_if_empty_does_not_wipe_existing_recipes():
    seed_if_empty()
    extra = crud.create_recipe(name="User Recipe", instructions="Keep me.")
    seed_if_empty()
    names = {r.name for r in crud.list_recipes()}
    assert extra.name in names
    assert "Classic Pancakes" in names
```

- [ ] **Step 2: Run test to verify it fails**

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/test_seed.py -q --tb=short
```

Expected: FAIL — second `seed_database()` leaves Weekly Meal Plan with 0 recipe links (cascade) and the orphan shopping list still present.

- [ ] **Step 3: Write minimal implementation**

In `meal_planner_app/seed_db.py`:

- Import `get_dao` from `meal_planner_app.crud` (keep existing `create_recipe`, `reset_recipes_db` import only if still used; **stop calling `reset_recipes_db` from `seed_database`**).
- Replace `seed_database` body:

```python
def seed_database():
    """Wipe all tables, then insert RECIPES_TO_SEED and Weekly Meal Plan.

    Used by POST /api/test/seed-db (E2E). Not used for persistent-DB startup
    (that is seed_if_empty).
    """
    print("Resetting database...")
    get_dao().reset()

    print(f"Seeding database with {len(RECIPES_TO_SEED)} recipes...")
    for recipe_data in RECIPES_TO_SEED:
        create_recipe(**recipe_data)

    print("Database seeding complete!")
    seed_meal_plans()
```

Leave `seed_meal_plans` and `seed_if_empty` unchanged. After `reset()`, no Weekly plan exists, so `seed_meal_plans` will create it with current recipe IDs.

- [ ] **Step 4: Run tests to verify they pass**

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/test_seed.py meal_planner_app/tests/test_crud.py -q --tb=short
```

Expected: PASS, including existing `test_seed_if_empty_is_idempotent`.

- [ ] **Step 5: Commit**

```bash
git add meal_planner_app/seed_db.py meal_planner_app/tests/test_seed.py .ai/next_step.md
git commit -m "$(cat <<'EOF'
fix(seed): reset all tables before E2E seed-db

seed_database now calls dao.reset() so Weekly Meal Plan is recreated with
the new recipe IDs instead of left empty after ON DELETE CASCADE.
EOF
)"
```

---

### Task 2: Meal-plan PUT and add-recipe honesty (A2)

**Files:**
- Modify: `meal_planner_app/main.py` (`api_update_meal_plan`, `api_add_recipe_to_meal_plan`)
- Modify: `meal_planner_app/crud.py` (`add_recipe_to_meal_plan` — return `None` if recipe missing)
- Modify: `meal_planner_app/tests/test_api.py` (new tests)
- Modify: `meal_planner_app/tests/test_crud.py` only the existing missing-recipe assertion (lines ~198–208 on origin/main)

- [ ] **Step 1: Write the failing tests**

Add to `TestApi` in `meal_planner_app/tests/test_api.py` (class already has `recipe1` / `recipe2` in meal-plan tests via setUp in that class — check `TestApi` vs nested classes; put tests on the same class as `test_update_meal_plan_api`):

```python
    def test_update_meal_plan_api_name_only_preserves_recipes(self):
        mp = crud.create_meal_plan(
            name="Keep Recipes",
            recipe_ids=[self.recipe1.recipe_id],
        )
        response = self.client.put(
            f"/api/meal-plans/{mp.meal_plan_id}",
            json={"name": "Renamed Only"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "Renamed Only")
        self.assertEqual(data["recipe_ids"], [str(self.recipe1.recipe_id)])
        self.assertEqual(len(data["recipes"]), 1)

    def test_add_missing_recipe_to_meal_plan_api_returns_404(self):
        mp = crud.create_meal_plan(name="My Plan")
        response = self.client.post(
            f"/api/meal-plans/{mp.meal_plan_id}/recipes",
            json={"recipe_id": str(uuid.uuid4())},
        )
        self.assertEqual(response.status_code, 404)

    def test_add_recipe_to_meal_plan_api_honors_count(self):
        mp = crud.create_meal_plan(name="My Plan")
        response = self.client.post(
            f"/api/meal-plans/{mp.meal_plan_id}/recipes",
            json={"recipe_id": str(self.recipe1.recipe_id), "count": 2.5},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        by_id = {r["id"]: r["count"] for r in data["recipes"]}
        self.assertEqual(by_id[str(self.recipe1.recipe_id)], 2.5)
```

In `test_crud.py`, change the missing-recipe case to expect `None`:

```python
        updated_mp_with_non_recipe = crud.add_recipe_to_meal_plan(
            mp.meal_plan_id, non_existent_recipe_id
        )
        self.assertIsNone(updated_mp_with_non_recipe)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest \
    meal_planner_app/tests/test_api.py::TestApi::test_update_meal_plan_api_name_only_preserves_recipes \
    meal_planner_app/tests/test_api.py::TestApi::test_add_missing_recipe_to_meal_plan_api_returns_404 \
    meal_planner_app/tests/test_api.py::TestApi::test_add_recipe_to_meal_plan_api_honors_count \
    -q --tb=short
```

Expected: name-only PUT returns `recipe_ids: []`; missing recipe returns 200; count stays 1.0.

If `TestApi` has no `self.recipe1`, copy the setUp pattern from `test_update_meal_plan_api` (that method creates recipes in class setUp around line 278+). Read the class setUp before writing.

- [ ] **Step 3: Write minimal implementation**

`api_update_meal_plan` in `main.py` — only pass `recipes=` when the client sent the key:

```python
    name = data.get("name")
    description = data.get("description")

    kwargs = {"name": name, "description": description}
    if "recipes" in data or "recipe_ids" in data:
        recipes_input = data.get("recipes") or data.get("recipe_ids")
        kwargs["recipes"] = _normalize_recipe_entries(recipes_input)

    updated_meal_plan = crud.update_meal_plan(meal_plan_id, **kwargs)
```

`add_recipe_to_meal_plan` in `crud.py` — if recipe missing, return `None` (same as missing plan):

```python
    if not meal_plan or not recipe:
        return None
```

`api_add_recipe_to_meal_plan` in `main.py`:

```python
    recipe_id = uuid.UUID(data["recipe_id"])
    count = data.get("count", 1.0)
    try:
        count = float(count)
    except (TypeError, ValueError):
        abort(400, description="count must be a number.")
    meal_plan = crud.add_recipe_to_meal_plan(meal_plan_id, recipe_id, count=count)
    if not meal_plan:
        abort(404, description="Meal plan or recipe not found.")
    return jsonify(_meal_plan_to_dict(meal_plan))
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/test_api.py meal_planner_app/tests/test_crud.py -q --tb=short
```

Expected: PASS. Existing `test_update_meal_plan_api` still replaces recipes when `recipes` is sent.

- [ ] **Step 5: Commit**

```bash
git add meal_planner_app/main.py meal_planner_app/crud.py \
  meal_planner_app/tests/test_api.py meal_planner_app/tests/test_crud.py .ai/next_step.md
git commit -m "$(cat <<'EOF'
fix(api): preserve meal-plan recipes on name-only PUT

Omit recipes unless the client sent recipes or recipe_ids. Adding a missing
recipe now 404s; POST .../recipes honors count.
EOF
)"
```

---

### Task 3: Drop view-mode purchased checkboxes (A3)

**Files:**
- Modify: `frontend/src/components/ShoppingListView.jsx`
- Create: `frontend/src/shoppingListView.lock.test.js`
- Do **not** edit `leftover-chrome.test.js` (A4 owns that file).
- Keep source-recipe `title` / `data-testid="shopping-item-sources"` on the label.
- Keep `purchased: false` on newly added edit-mode rows (API field).

- [ ] **Step 1: Write the failing test**

Create `frontend/src/shoppingListView.lock.test.js`:

```javascript
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const SRC = join(
  dirname(fileURLToPath(import.meta.url)),
  "components",
  "ShoppingListView.jsx",
);

describe("ShoppingListView purchased UX", () => {
  it("does not render view-mode purchased checkboxes", async () => {
    const src = await readFile(SRC, "utf8");
    assert.equal(src.includes("handleTogglePurchased"), false);
    assert.equal(src.includes('type="checkbox"'), false);
    assert.match(src, /formatSourceRecipeNames/);
    assert.match(src, /shopping-item-sources/);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  node --test src/shoppingListView.lock.test.js
```

Expected: FAIL — `handleTogglePurchased` and `type="checkbox"` still present.

- [ ] **Step 3: Write minimal implementation**

In `ShoppingListView.jsx`:

1. Delete `handleTogglePurchased` entirely.
2. In the view-mode (`!editMode`) list item, remove the `<input type="checkbox" ... />`.
3. Keep the `<span>` with `formatItemLabel(item)`, `title={sourceTitle || undefined}`, and `data-testid` for sources.
4. Drop the `item.purchased ? "line-through ..."` class; use `text-gray-800` only (checkboxes were the only way to set purchased in the UI).
5. Leave edit-mode rows and `purchased: false` on `handleAddItem` unchanged.

- [ ] **Step 4: Run tests to verify they pass**

```bash
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  npm run test:unit
```

Expected: PASS, including shopping-list source tooltip tests if they exist as node tests. Playwright is not required for this task; do not change e2e unless a spec clicks a checkbox (none do on origin/main).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ShoppingListView.jsx \
  frontend/src/shoppingListView.lock.test.js .ai/next_step.md
git commit -m "$(cat <<'EOF'
fix(ui): drop non-persisting shopping-list purchased checkboxes

View-mode toggles never PUT. Remove the checkboxes; keep source-recipe
tooltips on item labels.
EOF
)"
```

---

### Task 4: MealPlanForm submit errors and formHint (A4)

**Files:**
- Modify: `frontend/src/components/MealPlanForm.jsx`
- Modify: `frontend/src/i18n/leftover-chrome.test.js`

- [ ] **Step 1: Write the failing test**

In `leftover-chrome.test.js`, add `MealPlanForm.jsx` to `FORBIDDEN`:

```javascript
  "MealPlanForm.jsx": [
    "Error loading form:",
    "Use decimals for fractions e.g. 0.5, 1.25. Each row selects a recipe",
  ],
```

- [ ] **Step 2: Run test to verify it fails**

```bash
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  node --test src/i18n/leftover-chrome.test.js
```

Expected: FAIL — both English strings still in `MealPlanForm.jsx`.

- [ ] **Step 3: Write minimal implementation**

Replace single `error` with `loadError` and `submitError`.

- Fetch `.catch` → `setLoadError(error.message)` (keep axios for now; B1 drops it).
- Submit `.catch` → `setSubmitError(error.response?.data?.error || error.response?.data?.detail || error.message)` (accept both Flask `error` and leftover `detail`).
- Early return **only** for `loadError`.
- After the `<h2>`, if `submitError`, render:

```jsx
        {submitError && (
          <p className="mb-4 text-red-600 bg-red-50 border border-red-200 rounded p-3">
            {submitError}
          </p>
        )}
```

- Replace the hardcoded hint paragraph with `{t("mealPlans.formHint")}`.
- Load-error early return copy: `{t("mealPlans.errorLoadPlan", { message: loadError })}` if that key exists; otherwise keep a `t()` key already in locales. Do **not** leave `"Error loading form:"` as a literal.

If `mealPlans.errorLoadPlan` is “Error loading meal plan: {{message}}”, that is acceptable for the load-failure screen.

- [ ] **Step 4: Run tests**

```bash
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  sh -c 'npm run test:unit && npm run i18n:check && npm run format-check'
```

Expected: PASS. If prettier fails, `npm run format` and include the result.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/MealPlanForm.jsx \
  frontend/src/i18n/leftover-chrome.test.js .ai/next_step.md
git commit -m "$(cat <<'EOF'
fix(ui): keep meal-plan form mounted on submit errors

Split load vs submit errors and use mealPlans.formHint instead of
hardcoded English.
EOF
)"
```

---

### Task 5: Vite PDF proxy (A5)

**Files:**
- Modify: `frontend/vite.config.js`
- Create: `frontend/src/vite-proxy.test.js`

- [ ] **Step 1: Write the failing test**

```javascript
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const CONFIG = join(dirname(fileURLToPath(import.meta.url)), "..", "vite.config.js");

describe("Vite dev proxy", () => {
  it("proxies API and PDF Flask paths", async () => {
    const src = await readFile(CONFIG, "utf8");
    assert.match(src, /["']\/api["']/);
    assert.match(src, /["']\/shopping-lists["']/);
    assert.match(src, /["']\/meal-plans["']/);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  node --test src/vite-proxy.test.js
```

Expected: FAIL — only `/api` is proxied.

- [ ] **Step 3: Write minimal implementation**

In `frontend/vite.config.js` `server.proxy`:

```javascript
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
      "/shopping-lists": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
      "/meal-plans": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
```

Do not proxy `/ui`. SPA routes stay on Vite.

- [ ] **Step 4: Run tests**

```bash
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  npm run test:unit
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/vite.config.js frontend/src/vite-proxy.test.js .ai/next_step.md
git commit -m "$(cat <<'EOF'
fix(dev): proxy shopping-list and meal-plan PDF paths through Vite

PDF hrefs are /shopping-lists/:id/pdf, not under /api, so local :5173
downloads 404ed.
EOF
)"
```
