# .ai/next_step.md — Handoff

**Branch:** `feat/shopping-edit-order-by-location`
**Last updated:** 2026-09-09

## Standing instruction
Create a new branch only when starting **unrelated** work.

## This session

CI jobs `docker` and `test-in-container` still failed after c68e42e (`Acquire::Check-Valid-Until=false`). `apt-get update` succeeded, but GitHub's Fastly debian-security pool 404s:

```
Failed to fetch .../nss/libnss3_3.61-1%2bdeb11u7_amd64.deb  404  Not Found
```

Minimal fix in `.devcontainer/Dockerfile` only (same package list; no Debian/prod/bake refactor):

- Strip `debian-security` from `/etc/apt/sources.list` (`sed -i '/debian-security/d'`).
- Install Chromium runtime libs from bullseye main (+ updates). Drop Check-Valid-Until flags (main InRelease is fine).
- `python:3.9-bullseye` has security only in `sources.list` (empty `sources.list.d`).

Evidence:

- `docker run --rm python:3.9-bullseye` with the same sed + full package list → **APT_MAIN_ONLY_OK**. All debs from `http://deb.debian.org/debian bullseye/main` (libnss3 **2:3.61-1+deb11u3**, not the 404'ing `...+deb11u7`). No debian-security URLs.
- `docker buildx bake ci --load` → **exit 0**; apt layer used `sed -i '/debian-security/d'` and fetched libnss3 from bullseye/main; `#25 exporting to image` / `naming to docker.io/library/meal-planner:ci done`.

## Next

Unrelated remaining: auth; OpenAPI; recipe discovery; prep-time metadata; meal-plan calendar; meal-plan PDF.

## Out of scope

Machine-translating imported recipes; Flask-Babel; SQLite locale column; RTL; Jest/RTL.
