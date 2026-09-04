# Technology Stack

Technologies actually used in the Meal Planner as of **2026-09-02**. Discovery libraries remain recommendations only.

See `.ai/progress.md` for feature status.

## Backend Technologies

*   **Language:** Python 3.9 (bake default; CI `setup-python` matches)
*   **Framework:** Flask
    *   JSON API, PDF responses, static React at `/ui/`, legacy HTML GET **redirects** to `/ui/…`
    *   No Jinja templates / `render_template`
*   **PDF Generation:** fpdf2
    *   Used by persisted-list PDF (`/shopping-lists/<id>/pdf`) and meal-plan generated PDF (`/meal-plans/<id>/shopping-list/pdf`)
    *   Optional DejaVu (`fonts-dejavu-core` in images); otherwise latin-1 sanitization
*   **WSGI (prod/CI):** gunicorn
*   **Storage:** SQLite file (`MEAL_PLANNER_DB`, default `data/meal_planner.db`) behind nested DAOs in `meal_planner_app/dao/`. `crud.py` is the application facade (no SQL). Tests use `:memory:`.
*   **Packaging:** `pyproject.toml` (`Flask`, `fpdf2`; extras: pylint, pytest, black, pre-commit, gunicorn). Package-data: `static/**/*` only (no templates).

## Frontend Technologies

*   **Core Library:** React ^18.2.0
*   **DOM Rendering:** React DOM ^18.2.0
*   **Routing:** react-router-dom ^7 (basename `/ui`)
*   **HTTP:** axios ^1.11 (meal-plan components) and `fetch` (recipes, shopping, ingredients)
*   **HTML UI:** React SPA only. Jinja2 templating is decommissioned.

## Styling

*   **CSS Framework:** Tailwind CSS ^4.1 (`@tailwindcss/vite` in `frontend/`)
*   **CSS Processing:** PostCSS / Autoprefixer still listed in `frontend/package.json`; there is **no** leftover Jinja Tailwind v3 pipeline under `meal_planner_app/static/css/`

## Build Tools & Package Management

*   **Backend:** pip / setuptools (`pyproject.toml`)
*   **Frontend Build:** Vite ^7.1
*   **JS packages:** npm (`frontend/package-lock.json`; Dockerfiles use `npm ci`)
*   **Root `package.json`:** convenience `build:react` wrapper only (no `build:css` / Tailwind 3)
*   **Lint / format:**
    *   Backend: pylint + black (pre-commit)
    *   Frontend: ESLint 9 + prettier (`format`, `format-check`, `lint`)
*   **E2E:** Playwright (`@playwright/test` ^1.55)

## Development & Deployment Environment

*   **Containerization:** Docker Buildx bake (`docker-bake.hcl`)
    *   `dev` → `meal-planner:dev` / `meal-planner-dev` (`.devcontainer/Dockerfile`)
    *   `prod` → root `Dockerfile`
    *   `ci` → E2E image
*   **Node:** 20 (required by Vite 7 + Tailwind 4)
*   **Python:** 3.9
*   **Quality gates:** GitHub Actions `ci.yml` (native backend/frontend + bake smoke) and `integration-tests.yml` (Playwright in container)
*   **Start:** `start_and_seed.sh` (Flask/gunicorn + optional Vite + seed/migrate)

## Technology Recommendations for New Features

Aspirational. **Automatic Recipe Discovery is still not started.**

### Automatic Recipe Discovery *(Not Started)*

*   **Web Searching:** Google Custom Search JSON API (or similar), not SERP scraping.
*   **Crawling:** Requests + BeautifulSoup4; Scrapy only if crawl graphs appear.
*   **Extraction:** Prefer a dedicated LLM/API layer (see build-with-ai skill if implementing) over regex; spaCy/HF NER is an alternative.

Do not add these libraries until the feature is actually scheduled.

### Persistence *(Not Started)*

When leaving in-memory lists: SQLite is enough for single-user; Postgres if multi-instance. SQLAlchemy or a small repository layer around current dataclasses.

### Auth *(Not Started)*

Token auth (e.g. Flask-JWT or session + CSRF) only after there is a real multi-user need. Local single-user Docker can stay open.
