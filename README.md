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

## Production Deployment

The project includes a multi-stage `Dockerfile` to build a lean, secure image for production.

1.  **Build the production image:**
    From the root of the project, run:
    ```bash
    docker build -t meal-planner-app .
    ```

2.  **Run the production container:**
    ```bash
    docker run -d -p 5000:5000 --name meal-planner meal-planner-app
    ```
    The application will be available at `http://localhost:5000`. It runs using a Gunicorn WSGI server.
