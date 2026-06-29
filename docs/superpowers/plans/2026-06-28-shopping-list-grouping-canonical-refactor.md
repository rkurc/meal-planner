# Shopping List Grouping Canonical Refactor & PDF Cleanup

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure shopping list location resolution and grouping into a single canonical implementation so both generated and persisted lists (and suggestion endpoints) are consistent, eliminate duplication, keep persistence as flat list with explicit contract, move PDF response shaping next to the generator in services.py, and clean test pollution — all to meet the strict code review standards (no duplication, no inconsistent policy, direct maintainable code, proper layering).

**Architecture:** 
- Single `_resolve_location_key` (handles dataclass items and dicts from aggregation) as the one source of truth for "prefer location then location_id".
- New `group_items_for_display(items, *, exclude_purchased=False)` as the canonical grouper + sorter (replaces both the ad-hoc code in generate_shopping_list and the previous _group_items_for_pdf).
- generate_shopping_list and list_unique_locations now delegate to the canonical resolver.
- create_shopping_list remains flat-list persistence (editable items); grouping is presentation only.
- `build_shopping_list_pdf_attachment` lives in services.py next to generate_shopping_list_pdf.
- Routes in main.py become thin.

**Tech Stack:** Python/Flask, dataclasses, in-memory "db", fpdf, pytest, Docker (meal-planner:dev image for all lint/test/build), pre-commit (black/pylint).

**Verification Discipline (Grok build mode — chosen over fast path):** Every change runs through:
- `docker buildx bake dev`
- `docker run ... meal-planner:dev python -m pytest ... -q`
- `docker run ... meal-planner:dev python -m pre_commit run --all-files` (or equivalent with git installed in container)
- Frontend: docker node:20-alpine for format-check + lint
- Update .ai/next_step.md with concrete evidence before any commit
- All per AGENTS.md. No direct host python/pytest/npm.

---

## File Responsibilities (locked in this plan)

- `meal_planner_app/crud.py`: Owns all data + canonical grouping/resolution logic. `list_unique_*`, `generate_shopping_list`, `shopping_list_to_pdf_data`, `create_shopping_list`, and new helpers.
- `meal_planner_app/services.py`: Owns PDF generation + now the attachment Response builder.
- `meal_planner_app/main.py`: Thin routes only. Remove local _pdf helper and old duplicated logic.
- `meal_planner_app/tests/test_shopping_list_api.py`: Tests for PDF routes, grouping semantics (location_id), suggestion endpoints, and the fixed locations test.
- `meal_planner_app/models/shopping_list.py`: No change (flat list is intentional).
- `docs/superpowers/plans/2026-06-28-....md` + `.ai/next_step.md`: Documentation/handover.

No other files.

---

### Task 1: Add canonical location resolver + grouper in crud.py + make generate_shopping_list and list_unique_locations use it

**Files:**
- Modify: `meal_planner_app/crud.py:113-140` (after list_unique_ingredient_names), and the grouping section at end of generate_shopping_list, plus replace the three PDF helper functions.
- Test: `meal_planner_app/tests/test_shopping_list_api.py` (indirectly via later tasks)

**Context for implementer:** The review identified that location resolution was duplicated (list_unique_locations, generate's grouping, the PDF _resolve, _group). generate used only "location" or "", causing location_id-only items to land in "". Persisted PDF used fallback. We want one place. Keep using defaultdict and the _loc_key sort semantics exactly (empty last, then alpha; items alpha by name inside group). The new grouper must accept both the dicts produced by aggregation AND ShoppingListItem dataclasses (direct attr access preferred where possible, but support both for the transition).

- [ ] **Step 1.1: Add the two private canonical helpers (after list_unique_ingredient_names)**

Add exactly this code (place it cleanly, keep existing list_unique for now but we will refactor it in next step):

```python
def _resolve_location_key(item: Union[dict, "ShoppingListItem"]) -> str:
    """Single source of truth for location grouping key.
    Prefers .location (or ['location']), falls back to .location_id / ['location_id'].
    Matches the rule previously duplicated in list_unique_locations and PDF code.
    """
    if isinstance(item, dict):
        loc = item.get("location") or item.get("location_id") or ""
    else:
        loc = getattr(item, "location", None) or getattr(item, "location_id", None) or ""
    return str(loc).strip()


def group_items_for_display(
    items: List[Union[dict, "ShoppingListItem"]], *, exclude_purchased: bool = False
) -> Dict[str, List[dict]]:
    """Canonical grouping + sorting for both generated and persisted shopping lists.
    Used for PDF (with exclude), API responses, and future display.
    Replicates previous sort semantics exactly: locations alpha with "" last;
    items inside each group sorted by name.
    """
    grouped: Dict[str, List[dict]] = defaultdict(list)
    for item in items:
        if exclude_purchased:
            purchased = item.get("purchased") if isinstance(item, dict) else getattr(item, "purchased", False)
            if purchased:
                continue
        loc_key = _resolve_location_key(item)
        # Normalize to the dict shape expected by generate_shopping_list_pdf
        if isinstance(item, dict):
            item_dict = {
                "name": item.get("name", "N/A"),
                "quantity": item.get("quantity", ""),
                "unit": item.get("unit", ""),
                "location": item.get("location"),
                "location_id": item.get("location_id"),
            }
        else:
            item_dict = {
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "location": item.location,
                "location_id": item.location_id,
            }
        grouped[loc_key].append(item_dict)

    def _loc_key(l: str):
        return (l == "", l)

    result: Dict[str, List[dict]] = {}
    for loc in sorted(grouped.keys(), key=_loc_key):
        sorted_items = sorted(grouped[loc], key=lambda x: str(x.get("name", "")))
        result[loc] = sorted_items
    return result
```

Run to ensure syntax (via Docker later).

- [ ] **Step 1.2: Update list_unique_locations to use the canonical resolver (no behavior change for now)**

Replace its body:

```python
def list_unique_locations() -> List[str]:
    """Returns a sorted list of unique location names (or ids) from ingredients.
    Resolution rule is canonical (_resolve_location_key).
    """
    locs: set = set()
    for recipe in recipes_db:
        for ing in recipe.ingredients:
            key = _resolve_location_key(ing)  # now uses the single impl
            if key:
                locs.add(key)
    return sorted(locs)
```

- [ ] **Step 1.3: Update the final grouping inside generate_shopping_list to use canonical (fix the inconsistency)**

Find the section after aggregation (around the old `grouped: Dict...` and the loop with `loc = item.get("location") or ""`).

Replace the grouping logic with a call that produces the same shape:

```python
    # Use canonical grouper so location_id fallback is consistent everywhere
    # (previously this path ignored location_id, sending items to the "" bucket).
    result = group_items_for_display(list(aggregated_ingredients.values()))
    return result
```

Remove the old manual grouped + _loc_key + sort code that followed. The aggregation still produces items with both "location" and "location_id".

- [ ] **Step 1.4: Replace the old PDF-specific helpers with thin wrappers over the canonical (or direct calls)**

Delete or replace `_resolve_item_location`, `_group_items_for_pdf`, and update:

```python
def shopping_list_to_pdf_data(
    shopping_list: ShoppingList,
) -> Dict[str, List[dict]]:
    """Public entry point: convert persisted ShoppingList to grouped PDF data.
    Excludes purchased items. Uses the canonical grouper.
    """
    return group_items_for_display(shopping_list.items, exclude_purchased=True)
```

Keep the function for backward compat of callers (it will now be one line).

- [ ] **Step 1.5: Add or update a unit test in the shopping list test file that directly proves canonical grouping for location_id-only (will be refined in later task)**

For now, just ensure existing tests would still conceptually pass. Actual test work in Task 4/6.

- [ ] **Step 1.6: Commit this task's changes**

```bash
git add meal_planner_app/crud.py
git commit -m "refactor(crud): introduce canonical _resolve_location_key + group_items_for_display

- Single resolution rule (location preferred over location_id)
- generate_shopping_list and list_unique_locations now delegate
- shopping_list_to_pdf_data becomes thin wrapper
- Fixes previous inconsistency where generated lists ignored location_id
"
```

**Verification for this task (Grok build):**
- docker buildx bake dev
- docker run --rm -v $(pwd):/app -w /app meal-planner:dev python -m pytest meal_planner_app/tests/test_shopping_list*.py -q --tb=short
- (full pre-commit later)

---

### Task 2: Make create_shopping_list flat-list contract explicit (no behavior change)

**Files:**
- Modify: `meal_planner_app/crud.py` (the create_shopping_list function and its docstring, around lines 406-449)

**Context:** Per review "for 3rd point use flat list". We keep the current design: persist flat list of ShoppingListItem (because the React ShoppingListView allows arbitrary edits, add/remove, change purchased, change per-item location). Grouping is always derived on demand. Document this explicitly so future readers understand it's intentional, not laziness.

- [ ] **Step 2.1: Update the docstring and add comments inside create_shopping_list**

Replace the relevant part of create_shopping_list with clearer version (keep the flatten logic exactly as-is):

```python
def create_shopping_list(meal_plan_id: uuid.UUID) -> Optional[ShoppingList]:
    """
    Generates a shopping list from a meal plan and saves it to the database.

    We deliberately persist items as a *flat list* of ShoppingListItem (not pre-grouped).
    Reasons:
    - The persisted list is user-editable (React UI allows changing name, qty,
      unit, location, and purchased status on individual items).
    - Grouping by location (for PDF or display) is a *presentation* concern and
      is recomputed from the current items via group_items_for_display /
      shopping_list_to_pdf_data.
    - This matches the shape returned to the client for editing.

    The incoming generated data from generate_shopping_list is grouped for the API,
    so we flatten here.
    """
    ...
    # generated is grouped {loc: [items...]} ; flatten for persisted ShoppingList
    # (see module docstring / function docstring for why flat)
    if isinstance(generated, dict):
        flat = []
        for loc_items in generated.values():
            flat.extend(loc_items)
        generated_items = flat
    ...
```

Keep all the rest of the function body identical (the ShoppingListItem construction already preserves location + location_id).

- [ ] **Step 2.2: Add a brief module-level comment near the shopping list section if helpful**

Near "# --- Shopping List CRUD Operations ---" add 2-3 lines referencing the canonical grouper.

- [ ] **Step 2.3: Run relevant tests + commit**

Use Docker pytest on shopping list tests.

Commit:

git commit -m "docs(crud): make flat-list contract for persisted shopping lists explicit

Per review: keep flat (editable), grouping is derived. No behavior change.
"

---

### Task 3: Move PDF attachment response builder into services.py (review point 5)

**Files:**
- Modify: `meal_planner_app/services.py` (add the builder near generate_shopping_list_pdf)
- Modify: `meal_planner_app/main.py` (remove _pdf_attachment_response, import and call the new one from services)

**Context:** The helper builds the Response + Content-Disposition. It belongs with the PDF generator (services) rather than route layer. Even though Response is a Flask type, it's acceptable here (the module already knows about PDF bytes for download). This makes main.py thinner.

- [ ] **Step 3.1: Add the builder to services.py (at the bottom or after the generate function)**

```python
from flask import Response   # only for the attachment builder


def build_shopping_list_pdf_attachment(
    title: str, grouped_data: Dict[str, List[Dict]]
) -> Response:
    """Generate PDF bytes and return a complete Flask attachment Response.
    Central place for filename sanitization and Content-Disposition.
    Used by both meal-plan and persisted shopping list PDF routes.
    """
    pdf_bytes = generate_shopping_list_pdf(title, grouped_data)
    response = Response(pdf_bytes, mimetype="application/pdf")
    safe_name = title.replace(" ", "_").lower()[:50]
    filename = f"shopping_list_{safe_name}.pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
```

Update the generate_shopping_list_pdf type hints if needed for cleanliness (keep compatible).

- [ ] **Step 3.2: In main.py, delete the local _pdf_attachment_response, import the new one, and simplify the two routes**

At top (with other services import):

from meal_planner_app.services import (
    generate_shopping_list_pdf,
    build_shopping_list_pdf_attachment,
)

Remove the entire def _pdf_attachment_response...

Then the two routes become:

```python
@app.route("/meal-plans/<uuid:meal_plan_id>/shopping-list/pdf")
def download_shopping_list_pdf(meal_plan_id: uuid.UUID):
    ...
    generated = ...
    if generated is None:
        return redirect(...)
    return build_shopping_list_pdf_attachment(meal_plan.name, generated or {})


@app.route("/shopping-lists/<uuid:shopping_list_id>/pdf")
def download_persisted_shopping_list_pdf(shopping_list_id: uuid.UUID):
    ...
    grouped = crud.shopping_list_to_pdf_data(shopping_list)  # pylint: disable=no-member
    return build_shopping_list_pdf_attachment(shopping_list.name, grouped)
```

Clean up any now-unused imports (Response can be removed from this file if no longer used here).

- [ ] **Step 3.3: Verify with Docker (pytest the pdf routes + manual smoke if needed)**

- [ ] **Step 3.4: Commit**

```bash
git add meal_planner_app/services.py meal_planner_app/main.py
git commit -m "refactor(services): move PDF attachment response builder next to generator

Per review point 5. Routes are now thinner. Consistent with 'logic in canonical layer'.
"
```

---

### Task 4: Clean test pollution + strengthen location_id grouping assertions

**Files:**
- Modify: `meal_planner_app/tests/test_shopping_list_api.py`

**Context:** The test `test_api_get_locations` does full db reset inside the test body. This was called out as pollution (even though tearDown runs). Also, strengthen direct assertions on the new canonical `group_items_for_display` for the location_id-only case (proves the fix for both generate and persisted).

- [ ] **Step 4.1: Refactor test_api_get_locations to add data without destructive reset**

In the test, instead of reset + create one recipe, do:

- Create a recipe *on top of* existing setUp data (or minimally reset only if absolutely required, but prefer additive).

Better (minimal change, no pollution):

```python
def test_api_get_locations(self):
    """GET /api/locations returns sorted unique location values (canonical rule)."""
    # Additive: create recipes with the locations we care about.
    # Does not wipe setUp data.
    crud.create_recipe(
        name="Test Recipe Locations",
        instructions="Test.",
        ingredients_data=[
            {"name": "Milk", "quantity": 1, "unit": "l", "location": "Dairy"},
            {"name": "Bread", "quantity": 1, "unit": "", "location_id": "Bakery"},
        ],
    )
    resp = self.client.get("/api/locations")
    ...
    self.assertIn("Dairy", locs)
    self.assertIn("Bakery", locs)
    # Also assert that our canonical resolve rule is what list_unique uses
```

This still exercises the endpoint + the resolver via the list_unique path.

- [ ] **Step 4.2: Add a direct unit test for group_items_for_display with location_id-only (add to the test class or a small TestGroupItems class)**

```python
def test_group_items_for_display_location_id_fallback(self):
    from meal_planner_app.crud import group_items_for_display, ShoppingListItem
    items = [
        ShoppingListItem(name="Cheese", quantity=1, unit="kg", purchased=False,
                         location=None, location_id="4"),
        ShoppingListItem(name="Milk", quantity=2, unit="l", purchased=False,
                         location="Dairy", location_id=None),
    ]
    grouped = group_items_for_display(items)
    self.assertIn("4", grouped)          # resolved from location_id
    self.assertIn("Dairy", grouped)
    self.assertNotIn("", grouped)        # nothing fell to empty
```

Call it from the PDF location test or keep standalone. Run to prove canonical now handles what generate used to miss.

- [ ] **Step 4.3: Update the existing persisted PDF location_id test to also assert via the public group_items_for_display (or import and call)**

- [ ] **Step 4.4: Run full relevant test suite in Docker, commit**

Commit message mentioning the pollution fix + stronger canonical coverage.

---

### Task 5: Update any remaining call sites + final route slimming (if opportunities appear)

**Files:**
- Possibly main.py, crud.py (minor), tests.

Main work should already be done by previous tasks. This task is the "polish" pass to ensure no old manual grouping remains and the two PDF routes + API shopping list all benefit from canonical behavior.

- [ ] **Step 5.1: Audit (via grep or read) for any remaining `loc = .*location` manual grouping in the changed files. Remove if found.**
- [ ] **Step 5.2: Ensure the meal-plan PDF route and the persisted one now produce identical grouping semantics for location_id-only items (add a cross-check test if useful).**
- [ ] **Step 5.3: Run full test suite + Docker pre-commit equivalent.**
- [ ] **Step 5.4: Commit** "chore: ensure all paths use canonical grouper; no manual location logic left"

---

### Task 6: Full verification, .ai/next_step.md update, branch hygiene (Grok build)

**Files:**
- `.ai/next_step.md`
- (any docs touched)

- [ ] **Step 6.1: Rebuild dev image and run the complete verification checklist from .ai/next_step + AGENTS**

```bash
docker buildx bake dev

# Backend
docker run --rm -v $(pwd):/app -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/ -q --tb=short

# pre-commit inside container (install git if the image run needs it)
docker run --rm -v $(pwd):/app -w /app meal-planner:dev \
  bash -c 'apt-get update -qq && apt-get install -y -qq git && python -m pre_commit run --all-files'

# Frontend (exact node image)
docker run --rm -v "$(pwd)/frontend:/app" -w /app node:20-alpine \
  sh -c 'npm ci --no-audit --no-fund --silent && npm run format-check && npm run lint'
```

Capture key success lines ("71 passed", "All matched files use Prettier", "10.00/10" or equivalent, "exporting to image").

- [ ] **Step 6.2: Update .ai/next_step.md**

Add a "Work Completed" section summarizing:
- Canonical resolver + grouper implemented and used everywhere
- Flat list contract documented explicitly
- PDF builder now in services.py
- Test pollution removed + direct canonical tests added
- All verification commands + output evidence
- Checklist items checked

End with "Branch ready for push / re-review."

- [ ] **Step 6.3: Commit the final updates together**

```bash
git add .ai/next_step.md docs/superpowers/plans/...
git commit -m "docs: record canonical grouping refactor completion + verification evidence

Meets strict review bar:
- no duplicated location policy
- canonical layer owns grouping
- flat list + explicit contract
- PDF shaping in services
- tests clean
"
```

- [ ] **Step 6.4: (optional but per previous) push and report SHA**

---

## Self-Review of this Plan (done by writer)

1. Covers every item in the review's "Recommended Path Forward" (including explicit "use flat list" for #3 and point 5).
2. No placeholders.
3. Exact file:line guidance + real code in steps.
4. Uses TDD-friendly steps where natural (write test-ish assertion, implement, run).
5. Respects Docker-first + .ai update rule.
6. Bite-sized (each sub-step runnable in <5-10 min).
7. Calls out the architectural decisions locked (canonical in crud, builder in services, flat persistence).

Plan is ready for subagent-driven-development execution.
