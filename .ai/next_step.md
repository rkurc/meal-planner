# .ai/next_step.md — Handoff

**Branch:** `refactor/a4-mealplan-form-errors`
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

A4 (MealPlanForm submit errors) done.

- Split `error` into `loadError` / `submitError` so a failed save no longer unmounts the filled form.
- Load failure still early-returns with `t("mealPlans.errorLoadPlan", { message: loadError })`.
- Submit failure shows an inline red banner (IngredientForm pattern).
- Replaced hardcoded English hint with `t("mealPlans.formHint")`.
- `leftover-chrome.test.js` now forbids `"Error loading form:"` and the decimals hint in `MealPlanForm.jsx`.

Verification (image `meal-planner:dev`; host `frontend/` bind-mount hides image `node_modules`, so host files were copied onto the image frontend while keeping image `node_modules`):

```bash
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  node --test src/i18n/leftover-chrome.test.js
# FAIL before impl: MealPlanForm.jsx still contains "Error loading form:"

docker run --rm -v "$(pwd):/work" -w /app/frontend meal-planner:dev \
  sh -c 'find /work/frontend -mindepth 1 -maxdepth 1 ! -name node_modules -exec cp -a {} /app/frontend/ \; && npm run test:unit && npm run i18n:check && npm run format-check && npm run lint'
# PASS: 26 unit tests, i18n:check ok, prettier --check ., eslint .
```

## Next

Continue Wave 1 (A1 seed reset, A2 meal-plan PUT, A3 drop checkboxes, A5 Vite PDF proxy) on separate branches. Then Plan B, then Plan C.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; second DAO backend; persisting purchased checkboxes; dropping axios (Plan B).
