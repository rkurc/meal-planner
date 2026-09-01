# Jinja UI Decommission Implementation Plan

> **Status (2026-09-02):** Tasks 1–6 complete on `feat/decommission-jinja-ui` (commits `5b2df09`, `a526cd8`, `789212c`, `e273724`, plus the docs commit). React at `/ui/` is the only HTML UI. **Task 7 (full Docker verification) is next** — do not claim the definition of done until that gate is observed.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make React at `/ui/` the only HTML UI, then delete Jinja templates, form routes, and the legacy Tailwind v3 CSS pipeline without dropping recipe search.

**Architecture:** Two sequential phases on one branch (two commits, optionally two PRs). Phase A adds search to `GET /api/recipes` and `RecipeList` (the only Jinja-only user feature). Phase B replaces remaining HTML GET routes with redirects into `/ui/…`, deletes templates and form POST handlers, rewrites tests, and removes the Jinja CSS build. Keep `/ui` as the SPA basename (do not move React to `/`). Keep both PDF routes. Do not add auth, a database, OpenAPI, or discovery.

**Tech Stack:** Flask + existing `crud.search_recipes`, React 18 + react-router-dom v7 (`useSearchParams`), pytest, Playwright, Docker bake (`meal-planner-dev` / `meal-planner:dev`).

---

## What is left (inventory)

React already covers recipe/meal-plan/shopping CRUD, counts, persisted lists, PDF of edited lists, ingredient list, and suggestion datalists. Jinja is only still required for **search**.

### User-facing gap (must close before delete)

| Feature | Jinja | React today | Action |
|---|---|---|---|
| Recipe search + ingredient filter | `GET /recipes?search_query=&filter_ingredient=` → `crud.search_recipes` | `RecipeList` always `GET /api/recipes` (unfiltered) | Add query params on the API + search form on `/ui/recipes` |

### Keep (not Jinja UI)

- All `/api/*` JSON routes
- `/ui` + `/ui/` + `/ui/<path>` SPA catch-all
- `GET /shopping-lists/<uuid>/pdf` (React download)
- `GET /meal-plans/<uuid>/shopping-list/pdf` (generated PDF; change the current “generate failed → redirect to HTML page” to `abort(404)`)
- `crud.search_recipes` (19 unit tests already exist)
- `migrate_legacy.parse_ingredients_from_text` (CSV ingest, not Jinja)

### Delete after Phase A

**HTML routes in `meal_planner_app/main.py` (lines 93–368):**

- `GET /` and `GET /recipes` (Jinja list + search)
- `GET/POST /recipes/new`, `GET /recipes/<uuid>`, `GET/POST /recipes/<uuid>/edit`, `GET/POST /recipes/<uuid>/delete`
- `GET /meal-plans`, `GET/POST /meal-plans/new`, `GET /meal-plans/<uuid>`, `GET/POST /meal-plans/<uuid>/edit`
- `GET/POST /meal-plans/<uuid>/add-recipe/<uuid>`, `…/remove-recipe/<uuid>`, `…/delete`
- `GET /meal-plans/<uuid>/shopping-list` (flattened HTML table)

**Templates (8 files):** `meal_planner_app/templates/{base,recipe_list,recipe_form,recipe_detail,meal_plan_list,meal_plan_form,meal_plan_detail,shopping_list_detail}.html`

**Helpers used only by Jinja:** `parse_ingredients_from_textarea`, `nl2br` template filter, `render_template` / `url_for` imports once unused.

**Tests that POST/GET HTML (5 in `test_api.py`):**

- `test_create_recipe_via_form`
- `test_edit_recipe_via_form`
- `test_delete_recipe_via_form`
- `test_create_meal_plan_via_form`
- `test_generate_shopping_list_route`

**CSS pipeline:** `meal_planner_app/static/css/src/input.css`, root `package.json` `build:css` (Tailwind 3), Dockerfile lines 83–88 (`npx tailwindcss@3 … output.css`).

### Out of scope (not required to decommission Jinja)

Automatic recipe discovery, master ingredient CRUD, auth, OpenAPI, persistent DB, moving the SPA off `/ui`, lean-prod (drop Node from the image), i18n, dead `IngredientDetail.jsx` (optional tiny cleanup only if touched).

---

## Approaches considered

1. **Two-phase (recommended):** Search API + React search first (tests green, feature not lost). Then delete Jinja and add GET redirects. Bisectable; CI stays green between commits.
2. **Single big-bang PR:** Same work, one commit. Faster, harder to review, easy to drop search by accident.
3. **Delete Jinja without search:** Smallest diff. Drops a working, tested feature. Rejected.

**Locked decisions**

- Search params on existing `GET /api/recipes`: `q` and `ingredient` (empty both → current “list all”).
- Do **not** add `/api/search`.
- Keep React `basename: "/ui"`. `GET /` redirects to `/ui/`.
- Old HTML **GET** paths 302 to the matching `/ui/…` page. **POST** form handlers are removed (405/404).
- On-the-fly shopping HTML is not rebuilt in React (persisted list on meal-plan detail is the replacement). Redirect `GET /meal-plans/<id>/shopping-list` → `/ui/meal-plans/<id>`.
- No g↔kg conversion, no calendar, no prep-time fields.

---

## File map

| File | Role |
|---|---|
| `meal_planner_app/main.py` | Add search query args on `api_get_recipes`; add GET redirects; delete HTML routes/helpers; PDF 404 |
| `frontend/src/components/RecipeList.jsx` | Search form; fetch `/api/recipes?q=&ingredient=` |
| `frontend/e2e/main.spec.js` | Search E2E using seeded Pancakes / Omelette |
| `meal_planner_app/tests/test_api.py` | Search API tests; redirect tests; delete 5 form tests |
| `meal_planner_app/templates/` | Delete directory |
| `meal_planner_app/static/css/` | Delete (Jinja-only) |
| `package.json` (repo root) | Drop `build:css` / Tailwind 3 deps (or delete file if unused) |
| `Dockerfile` | Remove legacy Tailwind v3 `RUN` |
| `pyproject.toml` | Drop `templates/**/*` from package-data |
| `.ai/progress.md`, `.ai/migration_plan.md`, `README.md` | Record Phase 3 done |

---

## Master checklist

### Phase A — search parity

- [x] `GET /api/recipes?q=` filters by name/description/ingredient (same as `search_recipes`)
- [x] `GET /api/recipes?ingredient=` filters by ingredient substring
- [x] Combined `q` + `ingredient` works
- [x] No params still returns **all** recipes
- [x] `/ui/recipes` has search + ingredient fields, submit, and clear
- [x] Empty search results still show the form and “Create New Recipe”
- [x] Playwright: search “Pancake” shows Classic Pancakes, not Simple Omelette
- [x] Playwright: ingredient “Cheese” shows Simple Omelette, not Classic Pancakes
- [x] Existing 19 `TestRecipeSearch` tests still pass (no `search_recipes` behavior change)

### Phase B — remove Jinja

- [x] `GET /` → 302 `/ui/`
- [x] `GET /recipes` → 302 `/ui/recipes`
- [x] `GET /recipes/<uuid>` → 302 `/ui/recipes/<uuid>`
- [x] `GET /meal-plans` → 302 `/ui/meal-plans`
- [x] `GET /meal-plans/<uuid>` → 302 `/ui/meal-plans/<uuid>`
- [x] `GET /meal-plans/<uuid>/shopping-list` → 302 `/ui/meal-plans/<uuid>`
- [x] `POST /recipes/new` no longer creates via form (not 200 HTML)
- [x] `meal_planner_app/templates/` gone
- [x] `parse_ingredients_from_textarea` and `nl2br` gone
- [x] PDF routes still return `%PDF` (`/shopping-lists/<id>/pdf` and `/meal-plans/<id>/shopping-list/pdf`)
- [x] Failed meal-plan PDF is 404, not a redirect to a deleted HTML view
- [x] Five Jinja form tests removed or replaced
- [x] Dockerfile no longer builds `static/css/dist/output.css`
- [x] Root `package.json` no longer has `build:css` / tailwind 3
- [x] `pyproject.toml` package-data no longer lists templates
- [x] Docs updated (progress, migration plan, README)
- [ ] Docker verification list all green (below) — Task 7; not claimed in the docs pass

---

## Verification list (run in Docker; do not use host python/npm)

Image: `meal-planner-dev` or `meal-planner:dev` after `docker buildx bake dev`. Frontend format/lint: same image or `node:20-alpine` per AGENTS.md.

### After Phase A

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner-dev \
  python -m pytest meal_planner_app/tests/test_api.py meal_planner_app/tests/test_crud.py -q --tb=short
# Expect: all pass, including new search API tests + existing 19 search unit tests

docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner-dev \
  sh -c 'npm ci --no-audit --no-fund --silent && npm run format-check && npm run lint'
# Expect: Prettier "All matched files" ; eslint exit 0
```

Playwright (needs gunicorn + `TESTING=true` as in `.github/workflows/integration-tests.yml`):

```bash
# After backend is up on :5000 with TESTING=true and seed:
docker exec -e BASE_URL=http://localhost:5000 -w /app/frontend <container> npx playwright test
# Expect: previous 9 tests + new search test(s) pass
```

Manual API smoke:

```bash
curl -s 'http://localhost:5000/api/recipes?q=pancake' | python -c 'import sys,json; d=json.load(sys.stdin); assert any("Pancake" in x["name"] for x in d)'
curl -s 'http://localhost:5000/api/recipes?ingredient=Cheese' | python -c 'import sys,json; d=json.load(sys.stdin); assert any("Omelette" in x["name"] for x in d)'
curl -s 'http://localhost:5000/api/recipes' | python -c 'import sys,json; d=json.load(sys.stdin); assert len(d)>=2'
```

### After Phase B (full gate)

```bash
docker buildx bake dev
# Expect: exporting to image ... DONE  (no tailwind v3 step required)

docker run --rm -v "$(pwd):/app" -w /app meal-planner-dev \
  python -m pytest meal_planner_app/tests/ -q --tb=short
# Expect: 78 minus 5 form tests plus new search/redirect tests; all green
# Roughly: 78 - 5 + ~8 = ~81 (count the functions; do not hard-code if slightly off)

docker run --rm -v "$(pwd):/app" -w /app meal-planner-dev \
  python -m black --check .

docker run --rm -v "$(pwd):/app" -w /app meal-planner-dev \
  python -m pylint --rcfile=.pylintrc meal_planner_app
# Expect: 10.00/10

docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner-dev \
  sh -c 'npm ci --no-audit --no-fund --silent && npm run format-check && npm run lint'

docker buildx bake prod
# Expect: DONE; the RUN that compiled static/css/dist/output.css is gone
```

HTTP after a running container:

```bash
curl -sI http://localhost:5000/ | grep -i location
# Expect: Location: .../ui/   (302)

curl -sI http://localhost:5000/recipes | grep -i location
# Expect: /ui/recipes

curl -s -o /tmp/sl.pdf -w "%{http_code} %{content_type}\n" \
  http://localhost:5000/shopping-lists/<id>/pdf
# Expect: 200 application/pdf ; file starts with %PDF

curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:5000/recipes/new
# Expect: 404 or 405, not 200 HTML
```

Grep gate (must be empty except comments/docs/this plan):

```bash
rg -n "render_template|parse_ingredients_from_textarea|nl2br" meal_planner_app --glob '!tests/**'
# Expect: no matches in main.py
```

---

## Task 1: API search on `GET /api/recipes`

**Files:**
- Modify: `meal_planner_app/main.py` (`api_get_recipes`)
- Test: `meal_planner_app/tests/test_api.py`

- [x] **Step 1: Write failing tests** (append to `TestApi` in `test_api.py`)

```python
    def test_get_recipes_api_search_by_q(self):
        crud.create_recipe(name="Classic Pancakes", instructions="Mix")
        crud.create_recipe(name="Simple Omelette", instructions="Fold")
        response = self.client.get("/api/recipes?q=pancake")
        self.assertEqual(response.status_code, 200)
        names = [r["name"] for r in response.get_json()]
        self.assertEqual(names, ["Classic Pancakes"])

    def test_get_recipes_api_filter_ingredient(self):
        crud.create_recipe(
            name="Pancakes",
            instructions="Mix",
            ingredients_data=[{"name": "Flour", "quantity": 1, "unit": "cup"}],
        )
        crud.create_recipe(
            name="Omelette",
            instructions="Fold",
            ingredients_data=[{"name": "Cheese", "quantity": 1, "unit": "oz"}],
        )
        response = self.client.get("/api/recipes?ingredient=Cheese")
        self.assertEqual(response.status_code, 200)
        names = [r["name"] for r in response.get_json()]
        self.assertEqual(names, ["Omelette"])

    def test_get_recipes_api_q_and_ingredient(self):
        crud.create_recipe(
            name="Cheese Omelette",
            instructions="Fold",
            ingredients_data=[{"name": "Cheese", "quantity": 1, "unit": "oz"}],
        )
        crud.create_recipe(
            name="Cheese Sandwich",
            instructions="Assemble",
            ingredients_data=[{"name": "Cheese", "quantity": 1, "unit": "oz"}],
        )
        response = self.client.get("/api/recipes?q=omelette&ingredient=Cheese")
        self.assertEqual(response.status_code, 200)
        names = [r["name"] for r in response.get_json()]
        self.assertEqual(names, ["Cheese Omelette"])

    def test_get_recipes_api_no_params_returns_all(self):
        crud.create_recipe(name="A", instructions="a")
        crud.create_recipe(name="B", instructions="b")
        response = self.client.get("/api/recipes")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
```

- [x] **Step 2: Run tests to verify they fail**

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner-dev \
  python -m pytest meal_planner_app/tests/test_api.py::TestApi::test_get_recipes_api_search_by_q -q --tb=short
```

Expected: FAIL (`names` is two recipes, not `["Classic Pancakes"]`).

- [x] **Step 3: Minimal implementation** in `api_get_recipes` (`main.py` ~454–458)

Replace the body with:

```python
@app.route("/api/recipes", methods=["GET"])
def api_get_recipes():
    """List recipes, optionally filtered with q / ingredient (Jinja search parity)."""
    query = (request.args.get("q") or "").strip()
    ingredient = (request.args.get("ingredient") or "").strip()
    if query or ingredient:
        recipes = crud.search_recipes(query=query, filter_ingredient=ingredient)
    else:
        recipes = crud.list_recipes()
    return jsonify([_recipe_to_dict(recipe) for recipe in recipes])
```

Do not change `search_recipes`. Empty `q` + empty `ingredient` must still list all (the `if query or ingredient` guard).

- [x] **Step 4: Run tests to verify they pass**

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner-dev \
  python -m pytest meal_planner_app/tests/test_api.py::TestApi -q --tb=short \
    -k "recipes_api"
docker run --rm -v "$(pwd):/app" -w /app meal-planner-dev \
  python -m pytest meal_planner_app/tests/test_crud.py::TestRecipeSearch -q --tb=short
```

Expected: PASS (new API tests + 19 existing search tests).

- [x] **Step 5: Commit**

```bash
git add meal_planner_app/main.py meal_planner_app/tests/test_api.py
git commit -m "feat: filter GET /api/recipes with q and ingredient query params"
```

---

## Task 2: React recipe search UI + E2E

**Files:**
- Modify: `frontend/src/components/RecipeList.jsx`
- Modify: `frontend/e2e/main.spec.js`

- [x] **Step 1: Write the failing E2E** at the end of `frontend/e2e/main.spec.js`

Seeded data (`seed_db.RECIPES_TO_SEED`): Classic Pancakes (Flour, Milk, …), Simple Omelette (Cheese, Eggs, …).

```javascript
test("should filter recipes by search query and ingredient", async ({ page }) => {
  await page.goto("/ui/recipes");
  await expect(
    page.getByRole("heading", { name: "Classic Pancakes" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Simple Omelette" }),
  ).toBeVisible();

  await page.fill("#recipe-search", "Pancake");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(
    page.getByRole("heading", { name: "Classic Pancakes" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Simple Omelette" }),
  ).not.toBeVisible();

  await page.getByRole("link", { name: "Clear" }).click();
  await expect(
    page.getByRole("heading", { name: "Simple Omelette" }),
  ).toBeVisible();

  await page.fill("#recipe-search", "");
  await page.fill("#ingredient-filter", "Cheese");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(
    page.getByRole("heading", { name: "Simple Omelette" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Classic Pancakes" }),
  ).not.toBeVisible();
});
```

- [x] **Step 2: Run E2E to verify it fails** (Playwright against `/ui/` as in CI). Expected: timeout on `#recipe-search` (not in the DOM).

- [x] **Step 3: Implement `RecipeList.jsx`**

Do not early-return before the search form when the list is empty (search-miss must still show controls).

```jsx
import React, { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import RecipeItem from "./RecipeItem";

const RecipeList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const q = searchParams.get("q") || "";
  const ingredient = searchParams.get("ingredient") || "";
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [qInput, setQInput] = useState(q);
  const [ingredientInput, setIngredientInput] = useState(ingredient);

  useEffect(() => {
    setQInput(q);
    setIngredientInput(ingredient);
  }, [q, ingredient]);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (ingredient) params.set("ingredient", ingredient);
    const qs = params.toString();
    fetch(qs ? `/api/recipes?${qs}` : "/api/recipes")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        setRecipes(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [q, ingredient]);

  const handleSearch = (event) => {
    event.preventDefault();
    const next = {};
    if (qInput.trim()) next.q = qInput.trim();
    if (ingredientInput.trim()) next.ingredient = ingredientInput.trim();
    setSearchParams(next);
  };

  const handleClear = () => {
    setQInput("");
    setIngredientInput("");
    setSearchParams({});
  };

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Recipes</h2>
        <Link
          to="/recipes/new"
          className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
        >
          Create New Recipe
        </Link>
      </div>
      <form
        onSubmit={handleSearch}
        className="mb-6 flex flex-wrap items-center gap-2"
      >
        <input
          id="recipe-search"
          type="text"
          value={qInput}
          onChange={(e) => setQInput(e.target.value)}
          placeholder="Search term..."
          className="px-3 py-2 border border-gray-300 rounded-md shadow-sm w-64"
        />
        <input
          id="ingredient-filter"
          type="text"
          value={ingredientInput}
          onChange={(e) => setIngredientInput(e.target.value)}
          placeholder="Filter by ingredient..."
          className="px-3 py-2 border border-gray-300 rounded-md shadow-sm w-52"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Search
        </button>
        {(q || ingredient) && (
          <Link
            to="/recipes"
            onClick={handleClear}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
          >
            Clear
          </Link>
        )}
      </form>
      {loading && <p className="text-center text-gray-500">Loading recipes...</p>}
      {error && (
        <p className="text-center text-red-500">Error loading recipes: {error}</p>
      )}
      {!loading && !error && recipes.length === 0 && (
        <p className="text-center text-gray-500">No recipes found.</p>
      )}
      {!loading && !error && recipes.length > 0 && (
        <ul className="space-y-4">
          {recipes.map((recipe) => (
            <RecipeItem key={recipe.id} recipe={recipe} />
          ))}
        </ul>
      )}
    </div>
  );
};

export default RecipeList;
```

Clear control must be a **link** named “Clear” so the E2E `getByRole("link", { name: "Clear" })` matches. Existing tests use heading names “Classic Pancakes” / “Simple Omelette” via `RecipeItem` — keep that.

- [x] **Step 4: Format in Docker, then re-run E2E**

```bash
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner-dev \
  sh -c 'npm ci --no-audit --no-fund --silent && npm run format && npm run format-check && npm run lint'
```

Expected: Prettier clean, eslint 0. Playwright: 10 tests pass (9 old + search).

- [x] **Step 5: Commit**

```bash
git add frontend/src/components/RecipeList.jsx frontend/e2e/main.spec.js
git commit -m "feat: add recipe search and ingredient filter to React list"
```

---

## Task 3: Legacy GET redirects

**Files:**
- Modify: `meal_planner_app/main.py`
- Test: `meal_planner_app/tests/test_api.py`

Do this **before** deleting the HTML views, or in the same change as Task 4. Prefer replacing the Jinja handlers with redirects in one commit (Task 3+4 together) so `/recipes` is never both HTML and a redirect.

- [x] **Step 1: Write failing redirect tests**

```python
    def test_root_redirects_to_ui(self):
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].rstrip("/").endswith("/ui"))

    def test_legacy_recipes_list_redirects_to_ui(self):
        response = self.client.get("/recipes", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/ui/recipes", response.headers["Location"])

    def test_legacy_recipe_detail_redirects_to_ui(self):
        recipe = crud.create_recipe(name="R", instructions="x")
        response = self.client.get(
            f"/recipes/{recipe.recipe_id}", follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/ui/recipes/{recipe.recipe_id}", response.headers["Location"])

    def test_legacy_meal_plans_list_redirects_to_ui(self):
        response = self.client.get("/meal-plans", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/ui/meal-plans", response.headers["Location"])

    def test_legacy_meal_plan_detail_redirects_to_ui(self):
        mp = crud.create_meal_plan(name="Plan")
        response = self.client.get(
            f"/meal-plans/{mp.meal_plan_id}", follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            f"/ui/meal-plans/{mp.meal_plan_id}", response.headers["Location"]
        )

    def test_legacy_shopping_list_html_redirects_to_meal_plan_ui(self):
        mp = crud.create_meal_plan(name="Plan")
        response = self.client.get(
            f"/meal-plans/{mp.meal_plan_id}/shopping-list",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            f"/ui/meal-plans/{mp.meal_plan_id}", response.headers["Location"]
        )
        self.assertNotIn("shopping-list", response.headers["Location"].split("/ui/")[-1])
```

Until Task 4, `GET /recipes` still returns 200 HTML — tests fail with 200 != 302.

- [x] **Step 2: Confirm failure**

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner-dev \
  python -m pytest meal_planner_app/tests/test_api.py::TestApi::test_root_redirects_to_ui -q --tb=short
```

Expected: FAIL `200 != 302`.

---

## Task 4: Remove Jinja routes, templates, helpers; fix PDF; drop form tests

**Files:**
- Modify: `meal_planner_app/main.py`
- Delete: `meal_planner_app/templates/` (all 8 html files)
- Modify: `meal_planner_app/tests/test_api.py` (remove 5 form tests; keep redirect tests from Task 3)

- [x] **Step 1: Delete the five HTML-form tests** in `test_api.py`:
  - `test_create_recipe_via_form`
  - `test_edit_recipe_via_form`
  - `test_delete_recipe_via_form`
  - `test_create_meal_plan_via_form`
  - `test_generate_shopping_list_route`

API coverage already exists: `test_create_recipe_api`, `test_update_recipe_api`, `test_delete_recipe_api`, `test_create_meal_plan_api`, `test_get_shopping_list_api`.

- [x] **Step 2: Replace HTML view functions in `main.py` with GET-only redirects**

Remove `parse_ingredients_from_textarea`, `nl2br`, and every `render_template` call.

Keep `remove_trailing_slash` (still useful for `/api` and PDFs). Keep `_pdf_attachment_response` and both PDF routes.

Suggested block to put **above** `# --- API Routes ---` (delete the old recipe/meal-plan HTML section entirely):

```python
def _redirect_ui(path: str):
    """302 into the React SPA. path is like '/recipes' or '/meal-plans/<id>'."""
    target = "/ui" + path if path.startswith("/") else "/ui/" + path
    return redirect(target, code=302)


@app.route("/")
def root():
    return redirect("/ui/", code=302)


@app.route("/recipes")
def legacy_recipe_list():
    return _redirect_ui("/recipes")


@app.route("/recipes/new")
def legacy_recipe_new():
    return _redirect_ui("/recipes/new")


@app.route("/recipes/<uuid:recipe_id>")
def legacy_recipe_detail(recipe_id: uuid.UUID):
    return _redirect_ui(f"/recipes/{recipe_id}")


@app.route("/recipes/<uuid:recipe_id>/edit")
def legacy_recipe_edit(recipe_id: uuid.UUID):
    return _redirect_ui(f"/recipes/{recipe_id}/edit")


@app.route("/meal-plans")
def legacy_meal_plan_list():
    return _redirect_ui("/meal-plans")


@app.route("/meal-plans/new")
def legacy_meal_plan_new():
    return _redirect_ui("/meal-plans/new")


@app.route("/meal-plans/<uuid:meal_plan_id>")
def legacy_meal_plan_detail(meal_plan_id: uuid.UUID):
    return _redirect_ui(f"/meal-plans/{meal_plan_id}")


@app.route("/meal-plans/<uuid:meal_plan_id>/edit")
def legacy_meal_plan_edit(meal_plan_id: uuid.UUID):
    return _redirect_ui(f"/meal-plans/{meal_plan_id}/edit")


@app.route("/meal-plans/<uuid:meal_plan_id>/shopping-list")
def legacy_shopping_list_html(meal_plan_id: uuid.UUID):
    return _redirect_ui(f"/meal-plans/{meal_plan_id}")
```

Do **not** keep POST aliases for `/recipes/new`, `/delete`, `/add-recipe`, etc.

Update `download_shopping_list_pdf` so a missing generated list is 404, not a redirect to the deleted HTML page:

```python
    generated = crud.generate_shopping_list(meal_plan_id)
    if generated is None:
        abort(404)
    return _pdf_attachment_response(meal_plan.name, generated or {})
```

Drop unused imports: `render_template`, `url_for` (if unused), `Markup` / `escape` if only used by `nl2br`. Keep `redirect`, `abort`, `Response`, `send_from_directory`, `jsonify`.

Update the module docstring: Flask serves JSON API, PDF, and the React SPA at `/ui/`.

- [x] **Step 3: Delete templates**

```bash
rm -rf meal_planner_app/templates
```

- [x] **Step 4: Run pytest**

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner-dev \
  python -m pytest meal_planner_app/tests/ -q --tb=short
```

Expected: all pass. No collection errors. Redirect tests 302. PDF tests still 200 `application/pdf`.

- [x] **Step 5: pylint + black via Docker; commit**

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner-dev python -m black .
docker run --rm -v "$(pwd):/app" -w /app meal-planner-dev \
  python -m pylint --rcfile=.pylintrc meal_planner_app
# Expect 10.00/10. If unused-import, delete the import (do not disable).

git add meal_planner_app/main.py meal_planner_app/tests/test_api.py
git add -u meal_planner_app/templates
git commit -m "feat: decommission Jinja UI; redirect legacy GET paths to /ui/"
```

---

## Task 5: Remove Jinja CSS pipeline

**Files:**
- Modify: `Dockerfile` (delete lines 83–88, the `npx tailwindcss@3` RUN)
- Modify or delete: root `package.json`
- Delete: `meal_planner_app/static/css/` (`src/input.css` and any `dist/`)
- Modify: `pyproject.toml` package-data — change to static only:

```toml
[tool.setuptools.package-data]
meal_planner_app = ["static/**/*"]
```

Root `package.json` today:

```json
"build:css": "tailwindcss -i ./meal_planner_app/static/css/src/input.css -o ..."
"build": "npm run build:css && npm run build:react"
```

If nothing in CI/Docker calls root `npm run build`, delete root `package.json` **and** `package-lock.json` at repo root if present. If `build:react` is still a convenience script, keep the file with only:

```json
{
  "name": "meal_planner_app_frontend",
  "version": "0.1.0",
  "scripts": {
    "build:react": "npm --prefix frontend run build"
  }
}
```

No `tailwindcss` / `postcss` / `autoprefixer` in **root** `devDependencies` (frontend/ already has Tailwind 4).

- [x] **Step 1: Make the file edits**
- [x] **Step 2: `docker buildx bake prod`** — must succeed; log must **not** run `tailwindcss@3` against `input.css`
- [x] **Step 3: Commit**

```bash
git add Dockerfile pyproject.toml package.json
git add -u meal_planner_app/static/css
git commit -m "chore: remove Jinja Tailwind v3 CSS pipeline"
```

---

## Task 6: Docs + progress trackers

**Files:**
- Modify: `.ai/progress.md` — Jinja column: decommissioned; search: Done in React; Phase 3 done
- Modify: `.ai/migration_plan.md` — Phase 3 complete; leftover is auth/persistence (not migration)
- Modify: `.ai/implementation_summary.md`, `.ai/feature_summary.md`, `.ai/test_plan.md` (TC-FF-002 → Implemented in React)
- Modify: `.ai/next_step.md` — this plan executed; next is not Jinja
- Modify: `README.md` — dual UI line: React-only; `/` redirects to `/ui/`
- Modify: `meal_planner_app/README.md` — templates tree is gone

- [x] **Step 1: Apply the status edits** (no application logic)
- [x] **Step 2: Commit with the code** (AGENTS.md: next_step in the same commit as the work, or a follow-up docs commit on the same branch)

```bash
git add .ai README.md meal_planner_app/README.md docs/superpowers/plans/2026-09-01-jinja-decommission.md
git commit -m "docs: mark Jinja decommission complete; React is the only HTML UI"
```

---

## Task 7: Full verification (definition of done)

Run the **After Phase B** block in “Verification list” above. Do not claim done until:

- [ ] `docker buildx bake dev` and `prod` observed DONE
- [ ] pytest all green in the dev image
- [ ] black `--check` clean
- [ ] pylint 10.00/10
- [ ] frontend format-check + lint clean
- [ ] Playwright including the new search test
- [ ] `rg render_template meal_planner_app` has no `main.py` hits
- [ ] `GET /` 302 `/ui/`
- [ ] A persisted shopping-list PDF still starts with `%PDF`

---

## Spec coverage (self-review)

| Requirement | Task |
|---|---|
| Recipe search in React | 1 + 2 |
| Do not lose `search_recipes` semantics | 1 (no crud change) |
| Delete HTML routes/templates | 4 |
| Bookmark-friendly old URLs | 3 + 4 redirects |
| Keep PDFs | 4 (keep routes, 404 instead of HTML redirect) |
| Drop form tests | 4 |
| Drop Tailwind v3 / Dockerfile CSS | 5 |
| Docs | 6 |
| Docker evidence | 7 |
| Auth / DB / discovery | Explicitly out of scope |

No TBD/placeholder steps. Param names `q` / `ingredient` are consistent across API, React, and tests.
