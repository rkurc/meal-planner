# Meal Planner Application

This is a web application for managing recipes and meal plans. It features a Flask backend (full REST API) + dual UIs (complete legacy Jinja2 + modern React SPA with feature parity for recipes, meal plans, and shopping lists).

**Current reality (as of 2026-06-16):** 
- Full CRUD APIs + React for recipes, meal plans, shopping lists.
- 65 backend tests passing; 8 E2E.
- No Automatic Recipe Discovery or standalone ingredient master list (future).
- Dev via Docker strongly preferred for all checks (see AGENTS.md).
- Legacy UI coexists with React.

## Development

This project is configured to use a **VS Code Dev Container**, which provides a consistent, pre-configured development environment.

### Prerequisites

*   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   [Visual Studio Code](https://code.visualstudio.com/)
*   [Remote - Containers (VS Code Extension)](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Getting Started with the Dev Container

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Open in VS Code:**
    Open the cloned repository folder in Visual Studio Code.

3.  **Reopen in Container:**
    You will be prompted to "Reopen in Container". Click it. VS Code will build the development Docker image (as defined in `.devcontainer/Dockerfile`) and start the container.

4.  **Automatic Setup:**
    The `postCreateCommand` in the `devcontainer.json` will automatically install all required Python and Node.js dependencies. You can monitor the progress in the terminal.

### Development Workflow

Once the Dev Container is running, you can open a new terminal within VS Code (`Terminal > New Terminal`) to run the application.

*   **Run the Backend Server:**
    ```bash
    python -m meal_planner_app.main
    ```
    The Flask API server will be available at `http://localhost:5000`.

*   **Run the Frontend Dev Server:**
    For a better UI development experience with hot-reloading:
    ```bash
    npm run dev --prefix frontend
    ```
    The frontend will be available at `http://localhost:5173`. The Vite server is configured to proxy API requests to the backend.

*   **Run Backend Tests:** (All verifications via Docker dev image recommended)
    ```bash
    docker run --rm -v $(pwd):/app -w /app meal-planner-dev python -m pytest meal_planner_app/tests/ -q
    ```
    (65 tests currently pass.)

*   **Run Frontend E2E Tests:**
    Use Docker or ensure servers up. From project root:
    ```bash
    docker run --rm -v $(pwd)/frontend:/app/frontend -w /app/frontend meal-planner-dev npm run test
    ```
    (8 E2E tests for React flows.)

## Running with Docker on Windows (Recommended)

This project uses Docker for consistent builds and runs across environments. We use `docker buildx bake` (via `docker-bake.hcl`) to keep Node.js and Python versions in sync between the production `Dockerfile`, dev container, and CI.

### Prerequisites (Windows)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (enable WSL2 backend recommended)
- Git for Windows
- (Optional) [Visual Studio Code](https://code.visualstudio.com/) with Dev Containers extension for one-click dev

**Note on paths:** Use Windows-style paths with quotes for volume mounts, e.g. `C:\Users\YourName\path\to\legacy`.

### 1. Build the Image

From the project root:

```powershell
# Build the development image (includes dev tools, hot-reload, full dependencies)
docker buildx bake dev

# Or build the production image
docker buildx bake prod

# Override versions if needed (e.g. to match your CI)
NODE_VERSION=20.19 PYTHON_VERSION=3.10 docker buildx bake dev
```

This ensures the same Node 20+ (required by Vite 7 + Tailwind) and Python 3.9 are used everywhere.

### 2. Start the App (with Legacy Data Migration)

The container auto-starts the Flask backend (port 5000) + Vite frontend dev server (port 5173) and seeds the database.

To populate from legacy data, place either:
- `recipes.csv` (or `przepisy.csv`) — **recommended** (see section 5), or
- `przepisy_tmp.odb`

in your legacy folder (the script looks for files at `/app/legacy/...`):

```powershell
# Mount your legacy directory (replace with your actual path)
docker run -d `
  -p 5000:5000 `
  -p 5173:5173 `
  -v "C:\Users\YourName\path\to\your\legacy:/app/legacy:ro" `
  --name meal-planner-dev `
  meal-planner:dev
```

- Without the volume mount, it uses built-in seed data.
- The migration/seed runs automatically on start (via `start_and_seed.sh`).

View logs:
```powershell
docker logs -f meal-planner-dev
```

Stop:
```powershell
docker stop meal-planner-dev && docker rm meal-planner-dev
```

### 3. Connect from Windows Browser

- **React UI (recommended, with hot reload):** http://localhost:5173/ui/
- **API directly:** http://localhost:5000/api/recipes
- **React via backend (if using prod image static assets):** http://localhost:5000/ui/

The frontend proxies `/api/*` requests to the backend.

### 4. Running Natively (Without Docker, for Quick Local Dev)

```powershell
# Terminal 1: Backend
python -m meal_planner_app.main

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

- UI: http://localhost:5173/ui/
- API: http://localhost:5000

### 5. Recommended: 2-Step Legacy Migration (Reliable CSV Export)

The direct `.odb` reader is a heuristic (it reads raw binary HSQL data inside the ZIP). For clean, editable results we recommend the **2-step process**:

#### Step 1: Export from Windows (LibreOffice Base / OpenOffice Base)

1. Open your `przepisy_tmp.odb` file in LibreOffice Base.
2. In the left sidebar under **Tables**, locate the main recipes table (common names: `PRZEPISY`, `PRZEPIS`, `RECIPES`, `PRZEPISY_TMP`).
3. **Easiest method**:
   - Right-click the table → **Copy**.
   - Open LibreOffice Calc → Paste.
4. Or run a query: **Tools → SQL**, e.g. `SELECT * FROM PRZEPISY`, then copy the result grid to Calc.
5. In Calc:
   - Review / clean the data (fix names, make sure Polish characters look good).
   - Put ingredients in one column (recommended name: `ingredients`). One ingredient per line inside the cell (use Alt+Enter). Example cell content:
     ```
     500 g kurczak
     400 g dynia
     1 szt cebula
     ```
   - File → Save As → **Text CSV (.csv)**
     - **Character set**: UTF-8 (very important!)
     - Field delimiter: `,` (comma) or `;` (semicolon)
     - Text delimiter: `"`
     - Check **"Save column names"** / "Edit filter settings" if prompted.

Useful column names (the importer is flexible):
- `name`, `tytul`, `tytuł`, `nazwa`
- `source_url`, `url`, `zrodlo`, `źródło`
- `description`, `opis`
- `instructions`, `instrukcje`
- `ingredients`, `skladniki`, `składniki`

Save the file as `recipes.csv` (or `przepisy.csv`).

#### Step 2: Ingest the CSV

Mount your legacy folder and the CSV will be automatically picked up on container start (preferred over .odb):

```powershell
docker run -d `
  -p 5000:5000 -p 5173:5173 `
  -v "C:\path\to\your\legacy:/app/legacy:ro" `
  meal-planner:dev
```

Or run manually inside a running container:
```powershell
docker exec -it meal-planner-dev python -m meal_planner_app.migrate_legacy C:/.../recipes.csv
# or just the module name (it auto-detects common names)
```

The CSV route produces clean structured data (proper ingredients list with quantity/unit when possible).

### Direct .odb (still supported but not recommended)

```powershell
docker exec -it meal-planner-dev python -m meal_planner_app.migrate_legacy
```

This still works via heuristics but can produce truncated names and noisy ingredients from the binary storage format. Use CSV for production data.

### 6. Production Image

The `prod` target now installs Node.js + frontend dependencies in the final stage (to match the shared `start_and_seed.sh`).

```powershell
docker buildx bake prod
docker run -d `
  -p 5000:5000 `
  -p 5173:5173 `
  -v "C:\path\to\legacy:/app/legacy:ro" `
  --name meal-planner-prod `
  meal-planner:prod
```

This makes the default start script succeed (it will run both the Flask backend and Vite on 5173).

Access:
- React (via Vite): http://localhost:5173
- React (static assets via Flask): http://localhost:5000/ui/
- API: http://localhost:5000/api/recipes

**Note:** The prod image is now larger because it includes Node + dev dependencies. For a leaner true production deployment you can still override the command to use only gunicorn + the pre-built static files at `/ui/`.

### Troubleshooting (Windows + Docker)

- **Ports in use:** Stop other servers or change ports (`-p 5001:5000` etc.).
- **Volume mount not working:** Use full absolute Windows path in quotes. Ensure Docker Desktop has file sharing enabled for the drive.
- **npm not found or Node version error during build:** Always use `docker buildx bake` (it enforces Node 20+). Avoid plain `docker build` on the root Dockerfile if versions drift.
- **Hot reload not working:** Make sure you mounted the source volume for dev image: `-v "$(pwd):/app"`.
- **WSL2 issues:** Restart Docker Desktop or `wsl --shutdown`.
- **Legacy data not seeding:** Put `recipes.csv` (preferred) or `przepisy_tmp.odb` in the mounted legacy folder. See "Recommended: 2-Step Legacy Migration".
- **Build fails on Tailwind native bindings:** Use the bake command + Node 20 image (already handled in this setup).

For VS Code Dev Container (alternative to manual Docker):
- Install "Dev Containers" extension.
- Open the folder in VS Code → "Reopen in Container".
- It uses `.devcontainer/Dockerfile` + `postCreateCommand` for deps.
- Run commands inside the container terminal as above.

See `docker-bake.hcl` for how versions are centralized. Run `docker buildx bake --print` to inspect effective config.
