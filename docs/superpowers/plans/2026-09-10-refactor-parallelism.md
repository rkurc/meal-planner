# Refactor A/B/C — parallelism and execution order

> **For agentic workers:** Execute Wave 1 first (this file). Then Plan B, then Plan C. Use isolated git worktrees for parallel tasks. Do not run two implementers against the same files.

**Spec:** `docs/superpowers/specs/2026-09-10-codebase-review.md`  
**Plans:**

- A: `docs/superpowers/plans/2026-09-10-refactor-a-correctness.md`
- B: `docs/superpowers/plans/2026-09-10-refactor-b-simplification.md`
- C: `docs/superpowers/plans/2026-09-10-refactor-c-structural.md`

**A3 decision:** drop view-mode purchased checkboxes. Do not persist purchased.

---

## Dependency graph

```
A1 seed reset ─────────────┐
A2 meal-plan PUT ──────────┤
A3 drop checkboxes ────────┤──► Wave 1 complete ──► B1 api.js ──► B2 catalog hook
A4 MealPlanForm errors ────┤                         │
A5 Vite PDF proxy ─────────┘                         ├──► B3 ingredient GET collapse
                                                     ├──► B4 meal-plan names in JSON
C3 quarantine migrate_legacy (any time)              ├──► B5 JSON error handler
                                                     └──► B6 N+1 find_all
                                                              │
                                                              ▼
                                                         B7 E2E hygiene (needs A1)
                                                              │
                                                              ▼
                                                    C1 create_app ──► C2 split crud
                                                    C4 drop recipe_ids + Jinja 302s
                                                       (after B4)
```

## Waves

### Wave 1 — parallel (isolated worktrees)

These do **not** share production files:

| Task | Files | Conflicts with |
|---|---|---|
| A1 | `seed_db.py`, `tests/test_crud.py` (add tests only) | nothing in Wave 1 |
| A2 | `main.py`, `crud.py`, `tests/test_api.py`, `tests/test_crud.py` (add-recipe assertion) | A1 if both edit `test_crud.py` — **A2 must only add tests in `test_api.py` and change the existing add-missing-recipe assertion in `test_crud.py` after A1 lands, OR put the assertion change in the same hunk carefully.** Safer: A2 tests live in `test_api.py`; A2 still edits `test_crud.py` for the existing `test_add_recipe_to_meal_plan` missing-recipe case. **Do not run A1 and A2 in parallel if both touch `test_crud.py`.** Run A1 then A2 sequentially **or** A2 only changes `crud.py` + `main.py` + `test_api.py`, and A1 only changes `seed_db.py` + **new** `tests/test_seed.py`. **Chosen: A1 uses new `meal_planner_app/tests/test_seed.py`. A1 ∥ A2.** |
| A3 | `ShoppingListView.jsx`, `leftover-chrome.test.js` (or new source-lock test) | nothing |
| A4 | `MealPlanForm.jsx`, `leftover-chrome.test.js` | **A3 if both edit leftover-chrome.test.js** — A4 owns leftover-chrome additions for MealPlanForm; A3 uses a new `frontend/src/shoppingListView.lock.test.js` |
| A5 | `frontend/vite.config.js`, new `frontend/src/vite-proxy.test.js` | nothing |
| C3 | `migrate_legacy.py` move, `start_and_seed.sh`, tests import path | nothing in Wave 1 |

**Wave 1 parallel set:** A1, A2, A3, A4, A5, and optionally C3.

### Wave 2 — after Wave 1 merged

| Task | Depends on | Parallel with |
|---|---|---|
| B1 `api.js` + drop axios | A4 (MealPlanForm still uses axios until B1) | B6 |
| B2 catalog hook | B1 | B4, B5, B6 |
| B3 ingredient GET collapse | B1, B2 | B4, B5 after B1 |
| B4 meal-plan JSON names | A2 (PUT semantics stay) | B1–B3, B6 |
| B5 JSON errors | A2 | B1, B6 |
| B6 N+1 `find_all` | none (backend only) | **can start in Wave 1** if no one else edits `dao/sqlite.py` |
| B7 E2E hygiene | A1 | after B1 if tests use new client; else after A1 only |

**B6 can join Wave 1** (`dao/sqlite.py` + `tests/test_dao.py` only). Do that if capacity allows.

### Wave 3 — after Wave 2

| Task | Depends on |
|---|---|
| C1 `create_app()` | B5 (error handler lives on the app) |
| C2 split `crud.py` | B3/B4/B6 done so the split is of the new API, not the old one |
| C4 drop `recipe_ids` + Jinja 302s | B4 (frontend no longer sends `recipe_ids`) |

C3 may already be done in Wave 1.

---

## Merge order

1. Land Wave 1 branches onto `refactor/abc` (or stacked PRs: A1, A2, A3, A4, A5).
2. Land B6 whenever ready (independent).
3. Land B1 → B2 → B3; B4 and B5 can stack beside B2/B3.
4. B7 last in B.
5. C1 → C2; C4 after B4; C3 anytime.

Never start implementation on `main`. Work on `refactor/abc` or task branches from it.
