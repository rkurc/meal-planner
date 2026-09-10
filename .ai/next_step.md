# .ai/next_step.md — Handoff

**Branch:** `refactor/c1-create-app` (from `refactor/abc`)
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

C1 `create_app()` done.

| Task | SHA | Status |
|---|---|---|
| A1–A5 | on `refactor/abc` | done |
| B1–B7 | on `refactor/abc` | done |
| C3 quarantine migrate_legacy | `c68d916` / `eef6264` | done |
| C1 create_app | this commit | done |
| C2 split crud.py | next | pending |
| C4 drop recipe_ids + Jinja 302s | after C2 | pending |

### C1 done

`create_app(*, testing=False)` owns Flask construction. Module-level `app = create_app()` keeps gunicorn `meal_planner_app.main:app`.

`/api/test/seed-db` is registered only when `testing=True` or env `TESTING` is `1`/`true`/`yes`. The in-function 404 guard is gone. JSON `/api/` error handler from B5 is registered in the factory. DAO stays the `crud.get_dao()` singleton.

Verified:

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/ -q --tb=short
# 218 passed

docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pylint --rcfile=.pylintrc meal_planner_app/main.py
# 10.00/10
```

`test_seed_database_endpoint` now uses `create_app(testing=True).test_client()`.

## Next

C2: split `crud.py` into `domain/` modules with a compatibility re-export. Do not drop `recipe_ids` or Jinja 302s (C4). Do not bind DAO to the app.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; persisting purchased checkboxes.
SQL `GROUP BY` usage counts still a Python loop in `list_ingredients_summary`.
