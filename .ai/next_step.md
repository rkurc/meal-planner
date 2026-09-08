# .ai/next_step.md — Handoff

**Branch:** `feat/shopping-edit-order-by-location`
**Last updated:** 2026-09-08

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Shopping list **edit mode** now uses the same location grouping as view mode:

- `ShoppingListView` maps `groupItemsByLocation(editedItems)` in edit mode (named locations A–Z, Other last).
- Location section headings match view mode (`shopping.otherLocation` for blank/missing).
- Rows keep original item indexes so name/qty/unit/location/remove still mutate the right item.
- Changing a location re-groups the row immediately (same helper as view).

Tests:

- `shoppingListGroups.test.js`: display order + source check that edit mode does not `editedItems.map`.
- Playwright: `edit mode orders items by location like view mode` (Dairy → Pantry → Other; Milk/Flour/Salt; move Milk to Produce).
- `docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev npm run test:unit` → **16 pass**
- `npm run lint` / `format-check` / `i18n:check` in `meal-planner:dev` → clean
- Playwright in isolated verify container (`TESTING=true`, Vite :5173): shopping-lists.spec.js **2 passed**

Also: `frontend/.prettierignore` includes `test-results/` so format-check ignores Playwright artifacts.

## Next

Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata; meal-plan calendar; meal-plan PDF.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
