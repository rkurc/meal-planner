# .ai/next_step.md — Handoff

**Branch:** `feat/shopping-list-source-recipe-tooltips`
**Last updated:** 2026-09-09

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

Follow-up on Task 4 e2e: fail closed in
`generated items show source recipe names on hover title`.

- Require Generate after leftover lists are deleted
  (`await expect(generateButton).toBeVisible()` then click). No optional click.
- Shopping-lists GET must succeed (`expect(listsResp.ok())`); do not treat
  a failed GET as an empty list.
- Recipe-ID relink and Flour `title="Classic Pancakes"` kept.

Verification (`meal-planner:ci` mount, gunicorn `TESTING=true`, `--workers=1`):

```
docker.exe exec -e BASE_URL=http://localhost:5000 -e API_BASE_URL=http://localhost:5000 \
  -e PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
  -w /app/frontend meal-planner-e2e \
  npx playwright test e2e/shopping-lists.spec.js --workers=1
```

**4 passed (21.6s), 0 failed.** Includes hover-title after required Generate click.

## Next

This feature branch's planned tasks (aggregate → persist → tooltip → e2e)
are done.

Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata;
meal-plan calendar; meal-plan PDF.

Optional follow-up: `seed_database()` should reset meal plans and shopping
lists so E2E does not need to relink recipe IDs.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
