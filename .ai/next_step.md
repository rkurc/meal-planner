# .ai/next_step.md — Handoff

**Branch:** `feat/shopping-list-source-recipe-tooltips`
**Last updated:** 2026-09-09

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Task 4: Playwright coverage for shopping-list source-recipe titles.

- Added `generated items show source recipe names on hover title` in
  `frontend/e2e/shopping-lists.spec.js`. Asserts Flour (not Salt) has
  `data-testid="shopping-item-sources"` and `title="Classic Pancakes"`.
- Existing PDF test kept.
- Test setup relinks Weekly Meal Plan recipe IDs and deletes leftover
  shopping lists: `/api/test/seed-db` recreates recipes but keeps the
  meal plan, so IDs go stale and the previous spec's Location Order List
  would hide Generate.

Verification (UI baked from this worktree, `meal-planner:ci` mount, `--workers=1`):

```
docker.exe run --rm -v "$(wslpath -w "$(pwd)"):/app" -w /app/frontend \
  meal-planner:dev npm run build
# gunicorn in meal-planner-e2e (TESTING=true, worktree mounted)
docker.exe exec -e BASE_URL=http://localhost:5000 -e API_BASE_URL=http://localhost:5000 \
  -e PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
  -w /app/frontend meal-planner-e2e npx playwright test --workers=1
```

**18 passed (1.3m), 0 failed.** Includes the new hover-title test.

## Next

This feature branch's planned tasks (aggregate → persist → tooltip → e2e)
are done.

Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata;
meal-plan calendar; meal-plan PDF.

Optional follow-up: `seed_database()` should reset meal plans and shopping
lists so E2E does not need to relink recipe IDs.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
