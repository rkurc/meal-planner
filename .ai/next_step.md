# .ai/next_step.md — Handoff

**Branch:** `feat/decommission-jinja-ui` (do not switch branches for remaining decommission notes)
**Last updated:** 2026-09-02
**HEAD:** `7d63129` docs commit; this verification evidence is the next commit on the same branch

## Standing instruction
Create a new branch only when starting **unrelated** work.

## Context
Phase 3 of `.ai/migration_plan.md` is **complete**. React at `/ui/` is the only HTML UI. Task 7 (full Docker verification) **ran** on this tree. Status: **DONE_WITH_CONCERNS** — all gates green except Playwright full suite 9/10.

## Task 7 verification evidence (2026-09-02)

Image tags after bake: `meal-planner:dev` (`e2a963d1dd90`), `meal-planner:prod` (`8d7569bc5223`). Commands from repo root of this worktree. No host python/npm.

### 1. `docker buildx bake --load --progress=plain dev prod` — GREEN

```
#46 [dev] exporting to image
#46 naming to docker.io/library/meal-planner:dev done
#46 unpacking to docker.io/library/meal-planner:dev 2.8s done
#46 DONE 6.2s

#44 [prod] exporting to image
#44 naming to docker.io/library/meal-planner:prod done
#44 unpacking to docker.io/library/meal-planner:prod 5.0s done
#44 DONE 9.1s
```

No `tailwindcss@3` / `input.css` / `output.css` in the bake log.

### 2. pytest — GREEN (83 passed)

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/ -q --tb=short
```

```
83 passed, 4 warnings in 0.65s
```

Warnings are existing fpdf2 `ln=` deprecations in PDF tests only.

### 3. black --check — GREEN

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev python -m black --check .
```

```
All done! ✨ 🍰 ✨
15 files would be left unchanged.
```

### 4. pylint — GREEN

```bash
docker run --rm -v "$(pwd):/app" -w /app meal-planner:dev \
  python -m pylint --rcfile=.pylintrc meal_planner_app
```

```
Your code has been rated at 10.00/10
```

### 5. frontend format-check + lint — GREEN

```bash
docker run --rm -v "$(pwd)/frontend:/app/frontend" -w /app/frontend meal-planner:dev \
  sh -c 'npm run format-check && npm run lint'
```

```
> prettier --check .
All matched files use Prettier code style!
> eslint .
(exit 0)
```

### 6. Playwright — 9 passed, 1 failed (not green)

Pattern: CI/Task 2 — container `meal-planner-e2e-verify` from `meal-planner:dev`, `npx playwright install --with-deps`, `TESTING=true gunicorn --bind 0.0.0.0:5000`, seed, then:

```bash
docker exec -e BASE_URL=http://localhost:5000 -w /app/frontend \
  meal-planner-e2e-verify npx playwright test
```

| # | Test | Result |
|---|---|---|
| 1 | homepage has expected title | pass |
| 2 | navigate to recipes / seeded Classic Pancakes + Simple Omelette | pass |
| 3 | create a new recipe | pass |
| 4 | view recipe details | pass |
| 5 | edit an existing recipe | pass |
| 6 | delete a recipe | pass |
| 7 | generate shopping list from meal plan | pass |
| 8 | edit shopping list items | pass |
| 9 | auto-populate default unit… (recipe + shopping) | **FAIL** (timeout 30s waiting `#name`) |
| 10 | **filter recipes by search query and ingredient** (Task 2) | **pass** (643ms) |

Retry of test 9 alone failed the same way (not a one-off flake).

Cause (pre-existing, not introduced by Jinja deletion): Vite `frontend/vite.config.js` has `base: "./"`. Built `index.html` uses `./assets/index-….js`. Full-page `GET /ui/recipes/new` (the only spec that deep-links a nested SPA path) resolves assets as `/ui/recipes/assets/…` → **404**. Flask *does* serve `index.html` for that path (200). Client-side navigations from `/ui/recipes` still work, which is why tests 3–6 pass.

Confirmed:

```
GET /ui/recipes/new → 200 text/html (index.html)
GET /ui/recipes/assets/index-B_rOr2m4.js → 404
GET /ui/assets/index-B_rOr2m4.js → 200
```

Tiny follow-up (new branch, not this decommission): set Vite `base: "/ui/"` and re-bake so nested SPA bookmarks load JS.

### 7. `render_template` grep — GREEN

```
# ripgrep not on host; used workspace grep equivalent
# pattern render_template|parse_ingredients_from_textarea|nl2br
# path meal_planner_app
# Result: No matches found (including main.py)
```

### 8. `GET /` 302 `/ui/` — GREEN

Live gunicorn:

```
curl -sI http://localhost:5000/     → HTTP/1.1 302 FOUND  Location: /ui/
curl -sI http://localhost:5000/recipes → 302  Location: /ui/recipes
POST /recipes/new → 405
```

Flask test_client (volume-mounted `meal-planner:dev`): `GET /` → `302 /ui/`.

### 9. PDF `%PDF` — GREEN

- pytest: `test_download_persisted_shopping_list_pdf_happy_path` asserts `startswith(b"%PDF")` (part of the 83).
- Live gunicorn: `POST /api/shopping-lists` then `GET /shopping-lists/<id>/pdf` → `200 application/pdf`, `starts_with_%PDF= True`, magic `b'%PDF-1.3'`, len 15226.

## Next

1. **Unrelated** (new branch): fix nested SPA asset URLs (`vite.config.js` `base: "/ui/"`) so `goto("/ui/recipes/new")` E2E and bookmarks work; re-run Playwright 10/10.
2. Other follow-ups (also new branch): persistent DB, auth/OpenAPI, dead `IngredientDetail.jsx` / unused `GET /api/ingredients/info`, extra E2E gaps, master ingredients / discovery.

## Out of scope / notes
- Do not push unless asked.
- Keep `/ui` basename.
- Keep both PDF routes.
- Do not restore POST form aliases, Tailwind v3, Jinja CSS, or templates.
- No application behavior was changed in Task 7.
