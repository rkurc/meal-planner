# .ai/next_step.md — Handoff

**Branch:** `feat/shopping-edit-order-by-location`
**Last updated:** 2026-09-09

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

CI jobs `docker` (CI workflow) and `test-in-container` (Integration and E2E Tests) failed while building the ci/dev image from `.devcontainer/Dockerfile`:

```
E: Release file for http://deb.debian.org/debian-security/dists/bullseye-security/InRelease is expired
```

Minimal fix in `.devcontainer/Dockerfile` only (same package list; no Debian/prod/bake refactor):

- `apt-get update` → `apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update`
- Comment: bullseye-security InRelease can be expired in CI.

Evidence:

- `docker run --rm python:3.9-bullseye bash -c 'apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update && apt-get install -y --no-install-recommends libnss3 && echo APT_WORKAROUND_OK'` → **APT_WORKAROUND_OK** (bullseye-security InRelease fetched; libnss3 installed from debian-security).
- `docker buildx bake ci --load` → **exit 0**; apt layer ran the new flags; `#25 exporting to image` / `naming to docker.io/library/meal-planner:ci done`.

## Next

Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata; meal-plan calendar; meal-plan PDF.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
