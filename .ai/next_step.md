# .ai/next_step.md — Handoff

**Branch:** `feat/shopping-list-source-recipe-tooltips`
**Last updated:** 2026-09-09

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Task 3: view-mode native `title` tooltip for `source_recipe_names` on shopping-list items.

- `formatSourceRecipeNames(names)`: trim, drop blanks, join with `", "`; non-array → `""`.
- View-mode item label `span`: `title={... || undefined}`; `data-testid="shopping-item-sources"` only when title is non-empty.
- No tooltip in edit mode. `handleAddItem` includes `source_recipe_names: []`. No new i18n keys.

Verification (Docker `meal-planner:dev`, frontend volume mount):

```
npm run test:unit
npm run format-check
npm run lint
```

**21 passed, 0 failed.** New `formatSourceRecipeNames` tests failed first (missing export), then passed after implementation. format-check and lint clean.

## Next

This feature branch's planned tasks (aggregate → persist → tooltip) are done.

Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata; meal-plan calendar; meal-plan PDF.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
