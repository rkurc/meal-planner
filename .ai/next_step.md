# .ai/next_step.md — Handoff

**Branch:** `feat/i18n-chrome-pr2-6`
**Last updated:** 2026-09-05

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

i18n spec **PR-2 through PR-6** on one branch (after PR-1 fonts on main):

- PR-2: i18next init, EN|PL switcher, nav `t()`, Playwright `locale: en-US`, `npm run i18n:check` in CI + AGENTS.md
- PR-3/4: recipe, ingredient, meal-plan, shopping chrome translated
- PR-5: PDF `?lang=` + RFC 5987 `filename*` + SPA href `resolvedLanguage`
- PR-6: Playwright PL smoke; `.ai/progress.md` i18n chrome Done

## Next

Unrelated remaining: auth; OpenAPI; discovery. Optional: IngredientForm remaining copy, RecipeForm placeholder-hint interpolation.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL.
