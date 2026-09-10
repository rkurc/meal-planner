# .ai/next_step.md — Handoff

**Branch:** `refactor/c3-quarantine-migrate-legacy` (from `refactor/abc`)
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Plan C Task 3: moved the legacy importer out of the runtime package.

- `meal_planner_app/migrate_legacy.py` → `tools/migrate_legacy.py` (no runtime shim)
- Tests import `from tools.migrate_legacy import extract_from_csvs`
- `start_and_seed.sh` runs `python /app/tools/migrate_legacy.py` or `python tools/migrate_legacy.py`, still `|| seed_if_empty`
- `.odb` heuristic kept; CSV parsing unchanged

**Verify:**
```
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/test_migrate_legacy.py -q --tb=short
```
Result: `1 passed`

Docs (`README.md`, `docs/legacy_przepisy_schema.md`, historical plans) still mention `python -m meal_planner_app.migrate_legacy`.

## Next

Remaining Plan B: B3 (collapse ingredient GETs), B7 (E2E hygiene).
Remaining Plan C: C1 (`create_app`), C2 (split `crud.py`), C4 (drop `recipe_ids` + Jinja 302s; after B4).

Optional: update README / `docs/legacy_przepisy_schema.md` to `python tools/migrate_legacy.py`.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
