# .ai/next_step.md — Handoff

**Branch:** `refactor/abc`
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Codebase review of `origin/main` @ `c8b480e`. Report + A/B/C plans committed.

**A3 decision:** drop view-mode purchased checkboxes (do not persist).

Documents:

- `docs/superpowers/specs/2026-09-10-codebase-review.md`
- `docs/superpowers/plans/2026-09-10-refactor-parallelism.md`
- `docs/superpowers/plans/2026-09-10-refactor-a-correctness.md`
- `docs/superpowers/plans/2026-09-10-refactor-b-simplification.md`
- `docs/superpowers/plans/2026-09-10-refactor-c-structural.md`

**Wave 1 (parallel, isolated worktrees):** A1 seed reset, A2 meal-plan PUT, A3 drop checkboxes, A4 MealPlanForm errors, A5 Vite PDF proxy. Optional: B6 batch find_all, C3 move migrate_legacy.

**Then:** Plan B, then Plan C (C3 may already be done).

## Next

Execute Wave 1 from Plan A. Do not implement on `main`.

## Out of scope

Auth; OpenAPI; React Query; SQLAlchemy; second DAO backend; persisting purchased checkboxes.
