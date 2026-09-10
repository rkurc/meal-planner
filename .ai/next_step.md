# .ai/next_step.md — Handoff

**Branch:** `feat/shopping-list-source-recipe-tooltips`
**Last SHA (feature):** `02ccf38` (`test(e2e): require generate and fail if list cleanup cannot run`)
**Last updated:** 2026-09-10

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session (Task 5: Handoff + full verification)

Did not reset. Feature work already on the branch:

- `ee7ba8b` feat(shopping): attach source recipe names when aggregating lists
- `001172a` feat(shopping): persist source_recipe_names on list items
- `10a1603` feat(ui): tooltip source recipes on shopping list items
- `256c5d6` test(e2e): shopping list item title lists source recipe
- `02ccf38` test(e2e): require generate and fail if list cleanup cannot run

### Verification (`docker.exe`, volumes `$(wslpath -w "$(pwd)")`)

**pytest** (`meal-planner:dev`) — **160 passed**, 17 warnings in 1.81s:

```
docker.exe run --rm -v "$(wslpath -w "$(pwd)"):/app" -w /app meal-planner:dev \
  python -m pytest meal_planner_app/tests/ -q --tb=no
```

**frontend** (`meal-planner:dev`) — unit **21 passed / 0 failed**; lint ok; `i18n:check ok`; prettier `All matched files use Prettier code style!`:

```
docker.exe run --rm -v "$(wslpath -w "$(pwd)/frontend"):/app/frontend" \
  -w /app/frontend meal-planner:dev \
  sh -c 'npm run test:unit && npm run lint && npm run i18n:check && npm run format-check'
```

**pre-commit** (`meal-planner:dev`) — all hooks **Passed** on the second run (after trailing-whitespace):

The image has no `git` binary and `debian-security` InRelease is expired. Working invocation:

```
docker.exe run --rm -v "$(wslpath -w "$(pwd)"):/app" -w /app meal-planner:dev sh -c '
  sed -i "/debian-security/d" /etc/apt/sources.list
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq git >/dev/null
  git config --global --add safe.directory /app
  printf "#!/bin/sh\nexec python -m pylint \"\$@\"\n" > /usr/local/bin/pylint
  printf "#!/bin/sh\nexec python -m black \"\$@\"\n" > /usr/local/bin/black
  chmod +x /usr/local/bin/pylint /usr/local/bin/black
  python -m pre_commit run --all-files
'
```

First run: trailing-whitespace **Failed** and fixed 3 files (`docs/superpowers/specs/2026-09-04-i18n-design.md`, `docs/superpowers/specs/2026-09-04-persistent-sqlite-dao-design.md`, `meal_planner_app/static/fonts/DejaVu.LICENSE`). black Passed, pylint Passed.
Second run: trim trailing whitespace, fix end of files, check yaml, check for added large files, black, pylint — all **Passed**.

**Playwright** (`meal-planner:ci` mount, gunicorn `TESTING=true` `-w 1`, `--workers=1`) — **4 passed (6.6s), 0 failed**:

```
docker.exe run -d --rm --name meal-planner-e2e --entrypoint tail \
  -v "$(wslpath -w "$(pwd)"):/app" meal-planner:ci -f /dev/null
docker.exe exec -w /app/frontend meal-planner-e2e npm run build
docker.exe exec -d -e TESTING=true -e PYTHONPATH=/app \
  -e MEAL_PLANNER_DB=/tmp/meal_planner_e2e.db meal-planner-e2e \
  gunicorn -w 1 --bind 0.0.0.0:5000 meal_planner_app.main:app
# wait until curl -sf http://localhost:5000/api/recipes succeeds (ready after 1 try)
docker.exe exec -e PYTHONPATH=/app -e MEAL_PLANNER_DB=/tmp/meal_planner_e2e.db \
  meal-planner-e2e python -m meal_planner_app.seed_db
docker.exe exec -e BASE_URL=http://localhost:5000 -e API_BASE_URL=http://localhost:5000 \
  -e PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
  -w /app/frontend meal-planner-e2e \
  npx playwright test e2e/shopping-lists.spec.js --workers=1
```

```
Running 4 tests using 1 worker
  ✓ shopping lists are on meal plans, not a separate nav page (593ms)
  ✓ should generate a meal-plan shopping list, fetch its PDF, and delete it (1.2s)
  ✓ edit mode orders items by location like view mode (1.8s)
  ✓ generated items show source recipe names on hover title (2.2s)
  4 passed (6.6s)
```

`npm run build` wrote gitignored `meal_planner_app/static/react_app/` (not committed).

## Next

This feature branch's planned tasks (aggregate → persist → tooltip → e2e → handoff) are done.

Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata; meal-plan calendar; meal-plan PDF.

Optional follow-up: `seed_database()` should reset meal plans and shopping lists so E2E does not need to relink recipe IDs.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
