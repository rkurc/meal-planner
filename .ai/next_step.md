# .ai/next_step.md — Handoff

**Branch:** `refactor/a3-drop-checkboxes`
**Last updated:** 2026-09-10

## This session

A3: dropped view-mode purchased checkboxes (they never PUT). Did not add persistence.

- Lock test `frontend/src/shoppingListView.lock.test.js` forbids `handleTogglePurchased` and `type="checkbox"`; keeps `formatSourceRecipeNames` and `shopping-item-sources`.
- `ShoppingListView.jsx`: removed toggle helper and view-mode checkbox; labels stay `text-gray-800` with source-recipe tooltips. Edit-mode add still sets `purchased: false`.

**TDD evidence:**

```bash
# FAIL before implementation (handleTogglePurchased still present)
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  node --test src/shoppingListView.lock.test.js
# AssertionError: true !== false

# PASS after (src overlay keeps image node_modules; host playwright.config for e2e-workers)
docker run --rm \
  -v "$(pwd)/frontend/src:/app/frontend/src" \
  -v "$(pwd)/frontend/playwright.config.js:/app/frontend/playwright.config.js" \
  -w /app/frontend meal-planner:dev npm run test:unit
# tests 26, pass 26, fail 0

docker run --rm -v "$(pwd)/frontend/src:/app/frontend/src" -w /app/frontend meal-planner:dev npm run format-check
# All matched files use Prettier code style!

docker run --rm -v "$(pwd)/frontend/src:/app/frontend/src" -w /app/frontend meal-planner:dev npm run lint
# exit 0
```

Did not edit `leftover-chrome.test.js`, backend, MealPlanForm, or vite.config.js.

## Next

Continue Wave 1 (parallel, isolated worktrees): A1 seed reset, A2 meal-plan PUT, A4 MealPlanForm errors, A5 Vite PDF proxy. Optional: B6 batch find_all, C3 move migrate_legacy.

Then Plan B, then Plan C.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; second DAO backend; persisting purchased checkboxes.
