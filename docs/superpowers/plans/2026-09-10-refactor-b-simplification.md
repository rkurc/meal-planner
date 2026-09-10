# Refactor B — Targeted Simplification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Follow superpowers:test-driven-development. Docker-first via `meal-planner:dev`.

**Goal:** One HTTP helper on the frontend, one catalog-lookups hook, one ingredient list API, meal-plan JSON that includes recipe names, JSON error bodies, and batched DAO `find_all`.

**Architecture:** No new frameworks. `frontend/src/api.js` is a 40-line `fetch` wrapper. Backend serializers stay in `main.py` until Plan C. B6 only changes `dao/sqlite.py` stitch logic. Do not start this plan until Wave 1 (Plan A) is merged unless executing B6 alone (B6 may join Wave 1).

**Tech Stack:** Python 3.9, Flask, sqlite3, React 18, node:test, Docker `meal-planner:dev`.

**Spec:** `docs/superpowers/specs/2026-09-10-codebase-review.md` scope B.

**Do not:** add React Query, axios replacement libraries, SQLAlchemy, or split `crud.py` (that is Plan C).

**Depends on:** Plan A merged (except B6).

---

## File map

| File | Role |
|---|---|
| `frontend/src/api.js` | `api.get/post/put/del` + `ApiError` |
| `frontend/src/api.test.js` | Tests for JSON parse + non-OK throw (mock `globalThis.fetch`) |
| `frontend/src/hooks/useCatalogLookups.js` | Ingredients/locations/units + default-unit map |
| `frontend/src/components/IngredientLineFields.jsx` | Shared name/qty/unit/location row |
| `frontend/src/components/RecipeForm.jsx` | Use api + hook + row |
| `frontend/src/components/ShoppingListView.jsx` | Use api + hook + row |
| `frontend/src/components/MealPlanList.jsx` | Drop axios |
| `frontend/src/components/MealPlanForm.jsx` | Drop axios; stop sending `recipe_ids` |
| `frontend/src/components/MealPlanDetail.jsx` | Drop axios; use recipe `name` from plan JSON |
| `meal_planner_app/main.py` | Ingredient list objects; drop `/info`; meal-plan names; JSON errorhandler |
| `meal_planner_app/crud.py` | Usage counts via SQL if a DAO method is added; else keep Python loop until B6 |
| `meal_planner_app/dao/sqlite.py` | Batch-load lines in `find_all` |
| `meal_planner_app/dao/protocol.py` | Optional `usage_counts()` on IngredientDao |
| `frontend/package.json` | Remove `axios` after last import is gone |
| `frontend/e2e/*.spec.js` | Shared `seedDb(page)`; drop `waitForTimeout` |

---

### Task 1: `api.js` and drop axios (B1)

**Files:**
- Create: `frontend/src/api.js`, `frontend/src/api.test.js`
- Modify: `MealPlanList.jsx`, `MealPlanForm.jsx`, `MealPlanDetail.jsx` first (the only axios users)
- Modify: `frontend/package.json` (remove axios) **after** grep is clean
- Then regenerate lockfile **in Docker** per AGENTS.md if package.json changes

- [ ] **Step 1: Write failing tests** for `api.js` in `frontend/src/api.test.js`

```javascript
import { describe, it, beforeEach, afterEach } from "node:test";
import assert from "node:assert/strict";
import { api, ApiError } from "./api.js";

describe("api", () => {
  const originalFetch = globalThis.fetch;
  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it("returns parsed JSON on 200", async () => {
    globalThis.fetch = async () =>
      new Response(JSON.stringify({ id: "1" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    const data = await api.get("/api/recipes/1");
    assert.equal(data.id, "1");
  });

  it("returns undefined on 204", async () => {
    globalThis.fetch = async () => new Response(null, { status: 204 });
    const data = await api.del("/api/recipes/1");
    assert.equal(data, undefined);
  });

  it("throws ApiError with status and body.error on 409", async () => {
    globalThis.fetch = async () =>
      new Response(JSON.stringify({ error: "dup" }), {
        status: 409,
        headers: { "Content-Type": "application/json" },
      });
    await assert.rejects(
      () => api.post("/api/ingredients", { name: "Flour" }),
      (err) => err instanceof ApiError && err.status === 409 && err.message === "dup",
    );
  });
});
```

This test fails because `./api.js` does not exist.

- [ ] **Step 2: Run to verify fail**

```bash
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  node --test src/api.test.js
```

Expected: FAIL — cannot find module.

- [ ] **Step 3: Minimal `api.js`**

```javascript
export class ApiError extends Error {
  constructor(message, status, body) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

async function request(method, url, body) {
  const headers = {};
  const opts = { method, headers };
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const response = await fetch(url, opts);
  if (response.status === 204) {
    if (!response.ok) {
      throw new ApiError(response.statusText, response.status, null);
    }
    return undefined;
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.error || data.detail || response.statusText;
    throw new ApiError(message, response.status, data);
  }
  return data;
}

export const api = {
  get: (url) => request("GET", url),
  post: (url, body) => request("POST", url, body),
  put: (url, body) => request("PUT", url, body),
  del: (url) => request("DELETE", url),
};
```

Switch MealPlanList/Form/Detail from axios to `api.*`. Keep submit payload `recipes` (still may include `recipe_ids` until B4/C4 — **stop sending `recipe_ids` here** if Plan A2 is merged; the backend still accepts `recipes` only).

MealPlanForm submitError should use `err.message` from `ApiError`.

- [ ] **Step 4: Verify**

```bash
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  sh -c 'npm run test:unit && npm run lint'
```

Grep: no `from "axios"` under `frontend/src`. Then remove axios from `package.json` and regenerate lockfile:

```bash
docker run --rm -v "$(pwd)/frontend:/app" -w /app node:20-alpine \
  sh -c 'npm uninstall axios'
```

- [ ] **Step 5: Commit** `feat(ui): add api.js and drop axios`

---

### Task 2: `useCatalogLookups` + ingredient row (B2)

**Files:**
- Create: `frontend/src/hooks/useCatalogLookups.js`
- Create: `frontend/src/defaultUnit.js` with `applyDefaultUnit(row, field, value, defaultUnits)` (extract the duplicated if-name-empty-unit block)
- Create: `frontend/src/defaultUnit.test.js`
- Create: `frontend/src/components/IngredientLineFields.jsx`
- Modify: `RecipeForm.jsx`, `ShoppingListView.jsx` to consume them
- Stop fetching `/api/ingredients` (names) if summary is used; until B3, hook may still hit `/api/ingredients/summary` + `/api/locations` + `/api/units`

- [ ] **Step 1: Failing unit test** for `applyDefaultUnit` in `defaultUnit.test.js`

```javascript
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { applyDefaultUnit } from "./defaultUnit.js";

describe("applyDefaultUnit", () => {
  const units = { Milk: "cups" };

  it("fills unit when name is set and unit empty", () => {
    const row = { name: "", unit: "" };
    const next = applyDefaultUnit(row, "name", "Milk", units);
    assert.equal(next.unit, "cups");
    assert.equal(next.name, "Milk");
  });

  it("does not overwrite an existing unit", () => {
    const row = { name: "", unit: "tbsp" };
    const next = applyDefaultUnit(row, "name", "Milk", units);
    assert.equal(next.unit, "tbsp");
  });

  it("ignores non-name fields", () => {
    const row = { name: "Milk", unit: "" };
    const next = applyDefaultUnit(row, "quantity", "1", units);
    assert.equal(next.unit, "");
  });
});
```

- [ ] **Step 2: Run — fail (module missing)**

- [ ] **Step 3: Implement `applyDefaultUnit`, hook, and `IngredientLineFields`**

`applyDefaultUnit`:

```javascript
export function applyDefaultUnit(row, field, value, defaultUnits) {
  const next = { ...row, [field]: value };
  if (field !== "name" || !value || (row.unit && String(row.unit).trim())) {
    return next;
  }
  const defUnit = defaultUnits[value.trim()];
  if (defUnit) next.unit = defUnit;
  return next;
}
```

Hook: on mount, `api.get("/api/ingredients/summary")`, `api.get("/api/locations")`, `api.get("/api/units")`. Build `ingredientDefaultUnits` `{ [name]: unit }`. Return `{ knownIngredients: summaries.map(s => s.name), knownLocations, knownUnits, ingredientDefaultUnits }`.

`IngredientLineFields` props: `item`, `onChange(field, value)`, `onRemove`, `placeholders`, `listIds` (`known-ingredients` etc). RecipeForm and ShoppingListView still own datalists (ids must stay unique if both ever mount together — they do not today).

Wire RecipeForm + ShoppingListView. Delete the four duplicated fetch blocks.

- [ ] **Step 4: `npm run test:unit` + `npm run lint` + `npm run format-check`**

- [ ] **Step 5: Commit** `refactor(ui): share catalog lookups and ingredient line fields`

---

### Task 3: Collapse ingredient GET APIs (B3)

**Files:**
- Modify: `meal_planner_app/main.py` — `GET /api/ingredients` returns the summary object list; delete `GET /api/ingredients/info` (or make it 410); keep `GET /api/ingredients/<uuid>`
- Modify: `meal_planner_app/tests/test_ingredient_api.py` (today asserts string list)
- Modify: `meal_planner_app/tests/test_shopping_list_api.py` suggestion tests if they expect string[]
- Modify: frontend hook from B2 to use `/api/ingredients` only (no `/summary`)
- Keep `GET /api/ingredients/summary` as a **temporary alias** returning the same payload for one release, then delete in this same task if grep is clean after hook change (grep `ingredients/summary` and `ingredients/info` — should be tests + main only)

- [ ] **Step 1: Failing tests**

Change `test_ingredient_api.py` GET list test to expect `[{id, name, usage_count, unit, location}, ...]`. Add `test_get_ingredient_info_removed` expecting 404 on `/api/ingredients/info?name=Cocoa`.

- [ ] **Step 2: Run — fail (still string[] / 200 on /info)**

- [ ] **Step 3: Implementation**

`api_get_ingredients` calls `crud.list_ingredients_summary()` instead of `list_unique_ingredient_names`. Remove `api_get_ingredient_info`. Leave POST `/api/ingredients` as create (REST collision remains; document in comment; do not add `/catalog` path).

Optional: add `IngredientDao.usage_counts() -> Dict[UUID, int]` as one `SELECT ingredient_id, COUNT(*) FROM recipe_ingredients GROUP BY 1` and use it in `list_ingredients_summary`. Prefer this in the same task if it is small.

- [ ] **Step 4: pytest `test_ingredient_api.py` `test_shopping_list_api.py` + frontend unit**

- [ ] **Step 5: Commit** `refactor(api): return ingredient objects from GET /api/ingredients`

---

### Task 4: Meal-plan JSON includes recipe names (B4)

**Files:**
- Modify: `meal_planner_app/main.py` `_meal_plan_to_dict`
- Modify: `meal_planner_app/tests/test_api.py`
- Modify: `frontend/src/components/MealPlanDetail.jsx` — delete the `GET /api/recipes` join; render `entry.name`; wrap name in `<Link to={/recipes/${id}}>`
- Keep `recipe_ids` in the JSON until Plan C4

- [ ] **Step 1: Failing test**

```python
    def test_meal_plan_json_includes_recipe_names(self):
        mp = crud.create_meal_plan(
            name="Named",
            recipe_ids=[self.recipe1.recipe_id],
        )
        response = self.client.get(f"/api/meal-plans/{mp.meal_plan_id}")
        data = json.loads(response.data)
        self.assertEqual(data["recipes"][0]["id"], str(self.recipe1.recipe_id))
        self.assertEqual(data["recipes"][0]["name"], self.recipe1.name)
        self.assertEqual(data["recipes"][0]["count"], 1.0)
```

- [ ] **Step 2: Run — fail (`name` missing)**

- [ ] **Step 3: Implementation**

In `_meal_plan_to_dict`, resolve names with `crud.get_recipe(rid)` **or** a single `list_recipes()` map in the serializer if the plan has many entries. For one plan, a dict from `list_recipes()` is fine (dataset is small). Shape:

```python
{"id": str(rid), "name": recipe.name if recipe else "", "count": float(...)}
```

Missing recipe → `"name": ""` (do not 500).

MealPlanDetail: `recipesInPlan` from `mealPlan.recipes` directly; Link to `/recipes/:id`.

- [ ] **Step 4: pytest + frontend lint**

- [ ] **Step 5: Commit** `feat(api): include recipe names on meal-plan JSON`

---

### Task 5: JSON error handler (B5)

**Files:**
- Modify: `meal_planner_app/main.py`
- Modify: `meal_planner_app/tests/test_api.py` (one 400 body)
- Frontend already reads `ApiError.message` after B1

- [ ] **Step 1: Failing test**

```python
    def test_api_400_returns_json_error(self):
        response = self.client.post("/api/recipes", json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        data = json.loads(response.data)
        self.assertIn("error", data)
```

- [ ] **Step 2: Run — fail (HTML from Flask abort)**

- [ ] **Step 3: Implementation**

```python
from werkzeug.exceptions import HTTPException

@app.errorhandler(HTTPException)
def handle_http_exception(exc):
    if request.path.startswith("/api/"):
        return jsonify({"error": exc.description or exc.name}), exc.code
    return exc
```

Do not change PDF or `/ui` errors.

- [ ] **Step 4: pytest `test_api.py` `test_ingredient_api.py`**

- [ ] **Step 5: Commit** `fix(api): return JSON bodies for /api HTTP errors`

---

### Task 6: Batch `find_all` (B6) — may join Wave 1

**Files:**
- Modify: `meal_planner_app/dao/sqlite.py` (`_SqliteRecipeDao.find_all`, meal plan, shopping list)
- Modify: `meal_planner_app/tests/test_dao.py` — existing tests must still pass; add `test_find_all_recipes_includes_ingredient_lines` if missing

**Do not** change SQL schema.

- [ ] **Step 1: Failing test** (only if current tests would not catch a broken stitch)

If `test_dao.py` already asserts `find_all()[0].ingredients`, skip new tests and go to implementation **after** adding a test that two recipes each have their own lines (catches crossed joins):

```python
    def test_find_all_does_not_cross_ingredient_lines(self):
        # insert two recipes with different ingredient names via crud or dao
        all_recipes = self.dao.recipes.find_all()
        by_name = {r.name: r for r in all_recipes}
        self.assertEqual([i.name for i in by_name["A"].ingredients], ["Flour"])
        self.assertEqual([i.name for i in by_name["B"].ingredients], ["Milk"])
```

Use whatever names the test inserts.

- [ ] **Step 2: Run — this test may already pass (N+1 is correct, just slow). If it passes, keep it as a regression lock, then implement the batch query anyway (behavior-preserving refactor). TDD exception: add the lock test first (must pass on old code), then change implementation, re-run (must still pass).**

- [ ] **Step 3: Implementation**

`find_all` recipes: `SELECT * FROM recipes ORDER BY name` then one query:

```sql
SELECT ri.recipe_id, ri.quantity, ri.unit, ri.ingredient_id,
       i.name, i.default_unit, i.location, i.location_id
FROM recipe_ingredients ri
JOIN ingredients i ON i.id = ri.ingredient_id
ORDER BY ri.recipe_id, ri.position
```

Group in Python by `recipe_id`. Same pattern for `meal_plan_recipes` and `shopping_list_items`. `find_by_id` may keep the single-row query.

- [ ] **Step 4: pytest `test_dao.py` `test_crud.py` `test_api.py`**

- [ ] **Step 5: Commit** `perf(dao): batch-load child rows in find_all`

---

### Task 7: E2E hygiene (B7)

**Files:**
- Create: `frontend/e2e/helpers.js` with `export async function seedDb(page) { ... }`
- Modify: `frontend/e2e/main.spec.js`, `ingredients.spec.js`, `shopping-lists.spec.js` to use it
- Remove `waitForTimeout` in `main.spec.js`
- Register `page.once("dialog")` **before** the click that opens it
- Keep `workers: 1`
- Shopping generate: do not `if (visible)`; after A1, generate should appear on a fresh seed unless a previous test in the same worker left a list — A1 reset now deletes shopping lists, so **always expect generate, click it** (or always expect the list after generate)

- [ ] **Step 1: Failing test** — if you add `frontend/src/e2e-timeout.lock.test.js` that greps e2e specs for `waitForTimeout` and expects 0 matches, that fails until timeouts are gone.

```javascript
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const E2E = join(dirname(fileURLToPath(import.meta.url)), "..", "e2e");

describe("e2e hygiene", () => {
  it("does not use waitForTimeout", async () => {
    const { readdir } = await import("node:fs/promises");
    const files = (await readdir(E2E)).filter((f) => f.endsWith(".spec.js"));
    for (const f of files) {
      const src = await readFile(join(E2E, f), "utf8");
      assert.equal(src.includes("waitForTimeout"), false, f);
    }
  });
});
```

- [ ] **Step 2: Run — fail**

- [ ] **Step 3: Shared helper + replace timeouts with `expect(...).toBeVisible()`**

- [ ] **Step 4: `npm run test:unit`. Playwright only if `meal-planner:ci` is available; do not claim E2E green without running it.**

- [ ] **Step 5: Commit** `test(e2e): share seedDb helper and drop waitForTimeout`
