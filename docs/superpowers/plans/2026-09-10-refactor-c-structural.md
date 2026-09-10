# Refactor C — Structural Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Follow superpowers:test-driven-development. Docker-first via `meal-planner:dev`.

**Goal:** App factory with the test-seed route opt-in, `crud.py` split by aggregate with a compatibility re-export, `migrate_legacy` out of the runtime package, and drop leftover `recipe_ids` plus Jinja HTML 302s.

**Architecture:** Behavior-preserving moves. `create_app(testing=False)` owns Flask construction. `meal_planner_app/crud.py` becomes a thin re-export for one release, then callers switch. Do not touch `meal_planner_app/ingest/` (already a separate package).

**Tech Stack:** Python 3.9, Flask, pytest, gunicorn `meal_planner_app.main:app` must keep working (module-level `app = create_app()`).

**Spec:** `docs/superpowers/specs/2026-09-10-codebase-review.md` scope C.

**Depends on:** Plan B merged, except Task 3 (C3) which may run in Wave 1.

**Do not:** introduce SQLAlchemy, blueprints-for-their-own-sake beyond a clean factory, or a second DAO backend.

---

## File map

| File | Role |
|---|---|
| `meal_planner_app/main.py` | `create_app(*, testing=False)`; `app = create_app()` for gunicorn |
| `meal_planner_app/pdf.py` | Rename from `services.py` (or keep `services.py` as re-export for one commit) |
| `meal_planner_app/domain/recipes.py` | Recipe CRUD + search extracted from `crud.py` |
| `meal_planner_app/domain/meal_plans.py` | Meal-plan CRUD |
| `meal_planner_app/domain/shopping.py` | Generate + persist shopping lists |
| `meal_planner_app/domain/ingredients.py` | Master ingredient CRUD + summaries |
| `meal_planner_app/crud.py` | Re-export public names used by `main`, `seed_db`, tests |
| `tools/migrate_legacy.py` | Moved importer; `__main__` entry |
| `start_and_seed.sh` | Call `python -m tools.migrate_legacy` or `python tools/migrate_legacy.py` |
| `meal_planner_app/tests/test_migrate_legacy.py` | Update import path |
| `meal_planner_app/tests/conftest.py` | `app = create_app(testing=True)` if tests switch off `from main import app` |
| Dockerfile CMD | Unchanged: `meal_planner_app.main:app` |

---

### Task 1: `create_app()` (C1)

**Depends on:** B5 (JSON error handler) so the handler is registered inside the factory.

**Files:** `meal_planner_app/main.py`, tests that import `app`.

- [ ] **Step 1: Failing test** in `meal_planner_app/tests/test_app_factory.py`

```python
from meal_planner_app.main import create_app


def test_seed_route_absent_without_testing():
    app = create_app(testing=False)
    client = app.test_client()
    response = client.post("/api/test/seed-db")
    assert response.status_code == 404


def test_seed_route_present_when_testing():
    app = create_app(testing=True)
    client = app.test_client()
    # TESTING config is on; route is registered
    response = client.post("/api/test/seed-db")
    assert response.status_code == 200
```

The first test may already 404 without TESTING env (current guard). Change the design: **do not register the route at all** unless `testing=True` or `os.environ.get("TESTING")`. Then the failing part is: `create_app` does not exist (`ImportError`).

- [ ] **Step 2: Run — fail (`create_app` missing)**

- [ ] **Step 3: Implementation**

```python
def create_app(*, testing=False):
    app = Flask(__name__)
    if testing or os.environ.get("TESTING", "").lower() in ("1", "true", "yes"):
        app.config["TESTING"] = True
    # register before_request, routes, errorhandler, spa
    if app.config.get("TESTING"):
        app.add_url_rule("/api/test/seed-db", view_func=api_seed_database, methods=["POST"])
    return app


app = create_app()
```

Keep gunicorn target `meal_planner_app.main:app`. Bind DAO? **Out of scope** unless cheap: leave `crud.get_dao()` singleton.

Tests that do `from meal_planner_app.main import app` keep working because module-level `app` exists. Prefer `create_app(testing=True)` in new tests.

Remove the in-function 404 guard once the route is unregistered.

- [ ] **Step 4: Full pytest**

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/ -q --tb=short
```

- [ ] **Step 5: Commit** `refactor: add Flask create_app and opt-in seed route`

---

### Task 2: Split `crud.py` (C2)

**Depends on:** B3/B4/B6 so you split the post-simplification module.

**Files:** new `meal_planner_app/domain/*.py`, thin `crud.py`.

Public names that must keep importing from `meal_planner_app.crud` (grep before moving):

`set_dao`, `get_dao`, `create_recipe`, `get_recipe`, `update_recipe`, `delete_recipe`, `list_recipes`, `search_recipes`, `create_meal_plan`, `get_meal_plan`, `list_meal_plans`, `update_meal_plan`, `delete_meal_plan`, `add_recipe_to_meal_plan`, `remove_recipe_from_meal_plan`, `generate_shopping_list`, `shopping_list_to_pdf_data`, `create_shopping_list`, `get_shopping_list`, `list_shopping_lists`, `update_shopping_list`, `delete_shopping_list`, `list_unique_ingredient_names` (may already be unused after B3), `list_unique_locations`, `list_unique_units`, `list_ingredients_summary`, `get_recipes_for_ingredient`, `get_master_ingredient`, `get_master_ingredient_by_name`, `create_master_ingredient`, `update_master_ingredient`, `delete_master_ingredient`, `DuplicateIngredientNameError`, `IngredientInUseError`, `reset_recipes_db`, `reset_meal_plans_db`, `reset_shopping_lists_db`.

- [ ] **Step 1: Characterization** — run full pytest on current tree (must be green). No new tests required before the move. Add `tests/test_crud_exports.py`:

```python
import meal_planner_app.crud as crud

REQUIRED = [
    "get_dao",
    "create_recipe",
    "create_meal_plan",
    "generate_shopping_list",
    "create_master_ingredient",
    "DuplicateIngredientNameError",
]


def test_crud_reexports_public_names():
    for name in REQUIRED:
        assert hasattr(crud, name), name
```

This passes on the unsplit module (lock). After split it must still pass.

- [ ] **Step 2: Run — pass (lock)**

- [ ] **Step 3: Move functions** into `domain/recipes.py`, `domain/meal_plans.py`, `domain/shopping.py`, `domain/ingredients.py`. Shared `_dao` stays in `domain/_dao.py` (`set_dao`/`get_dao`). `crud.py`:

```python
"""Compatibility re-export. Prefer meal_planner_app.domain.* for new code."""
from meal_planner_app.domain.ingredients import *  # noqa: F401,F403
from meal_planner_app.domain.meal_plans import *  # noqa: F401,F403
from meal_planner_app.domain.recipes import *  # noqa: F401,F403
from meal_planner_app.domain.shopping import *  # noqa: F401,F403
from meal_planner_app.domain._dao import get_dao, set_dao
```

Prefer explicit `__all__` over star imports if pylint complains — then list every name.

Rename `services.py` → `pdf.py` and update `main.py` import. Leave `services.py` as:

```python
from meal_planner_app.pdf import *  # noqa
```

for one commit if tests import `services`; grep first. If only `main.py` imports it, skip the shim.

- [ ] **Step 4: Full pytest + pylint `meal_planner_app`**

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  sh -c 'python -m pytest meal_planner_app/tests/ -q --tb=short && pylint meal_planner_app'
```

- [ ] **Step 5: Commit** `refactor: split crud.py into domain modules with re-export`

---

### Task 3: Quarantine `migrate_legacy` (C3) — Wave 1 safe

**Files:**
- Move: `meal_planner_app/migrate_legacy.py` → `tools/migrate_legacy.py`
- Modify: `start_and_seed.sh`
- Modify: `meal_planner_app/tests/test_migrate_legacy.py` imports
- Modify: `pyproject.toml` if package-data / pytest paths need `tools`
- Do **not** change CSV parsing behavior
- `.odb` heuristic: keep in the moved file; do not delete in this task unless the move is trivial **and** tests still cover `extract_from_csvs` only

- [ ] **Step 1: Failing test** — change import in `test_migrate_legacy.py` to `from tools.migrate_legacy import extract_from_csvs` (or `import tools.migrate_legacy`). Run: fail (module missing).

Alternatively keep a shim:

```python
# meal_planner_app/migrate_legacy.py
from tools.migrate_legacy import *  # noqa
```

Prefer **no shim in the runtime package**. Tests and `start_and_seed.sh` switch together.

Need `tools/__init__.py` empty so `python -m tools.migrate_legacy` works if `tools` is a package. `start_and_seed.sh` can call:

```bash
python /app/tools/migrate_legacy.py
```

which does not need a package.

- [ ] **Step 2: Run test_migrate_legacy — fail**

- [ ] **Step 3: Move file, fix imports (`meal_planner_app.models` still importable), update shell**

`start_and_seed.sh` currently:

```bash
python -m meal_planner_app.migrate_legacy || \
    python -c "from meal_planner_app.seed_db import seed_if_empty; seed_if_empty()"
```

Change to:

```bash
python /app/tools/migrate_legacy.py || \
    python -c "from meal_planner_app.seed_db import seed_if_empty; seed_if_empty()"
```

On host without `/app`, use a path relative to repo root: `python tools/migrate_legacy.py`. Detect both:

```bash
if [ -f /app/tools/migrate_legacy.py ]; then
  python /app/tools/migrate_legacy.py
elif [ -f tools/migrate_legacy.py ]; then
  python tools/migrate_legacy.py
fi
```

Delete `meal_planner_app/migrate_legacy.py`.

- [ ] **Step 4: pytest `test_migrate_legacy.py` + grep no `meal_planner_app.migrate_legacy`**

- [ ] **Step 5: Commit** `refactor: move legacy importer out of the runtime package`

---

### Task 4: Drop `recipe_ids` JSON and Jinja 302s (C4)

**Depends on:** B4 (UI uses `recipes[].name` / `id` / `count` only). Grep frontend for `recipe_ids` — must be zero in `frontend/src` before deleting the serializer field.

**Files:** `main.py` (remove `_redirect_ui` routes and `recipe_ids` key), `MealPlanForm.jsx` (already stopped sending it in B1), tests in `test_api.py` that assert `recipe_ids` and legacy 302s.

- [ ] **Step 1: Failing tests** — update tests **first** to the new contract, watch old code fail:

`test_api.py`:
- Remove or invert `test_legacy_*_redirects_to_ui` — expect **404** (or 308 slash-normalizer only) for `GET /recipes`.
- `test_create_update_meal_plan_with_recipe_counts_api`: `self.assertNotIn("recipe_ids", data)`.

- [ ] **Step 2: Run — fail (302 still happens; `recipe_ids` still present)**

- [ ] **Step 3: Delete legacy route functions in `main.py` (~lines 67–109). Stop emitting `recipe_ids` in `_meal_plan_to_dict`. Keep accepting `recipe_ids` on **write** for one release (`data.get("recipes") or data.get("recipe_ids")`) so old clients do not wipe plans — document that in the function docstring.

- [ ] **Step 4: pytest `test_api.py` + frontend unit**

- [ ] **Step 5: Commit** `refactor(api): drop meal-plan recipe_ids and Jinja HTML redirects`

---

## Notes for implementers

- Gunicorn must keep `meal_planner_app.main:app`.
- `ingest/` is out of scope.
- Star-import `crud.py` is allowed for one release; pylint `disable=wildcard-import` on that file only.
- After C2, new code imports `domain.*`; do not add new functions to `crud.py`.
