## Development Environment

This project includes a Dev Container configuration, making it easy to get started with local development. The Dev Container comes with Python, Flask, Node.js, and npm pre-installed.


### Prerequisites

- Docker Desktop
- Visual Studio Code
- Remote - Containers (VS Code Extension)

### Getting Started (inside Dev Container)

1.  Clone the repository.
2.  Open the repository in Visual Studio Code.
3.  When prompted, click "Reopen in Container". This will build the Docker image (including Python and Node.js dependencies) and start the Dev Container.
4.  **Install/Update Application Dependencies (if needed after initial build or pulling changes)**:
    *   Python dependencies are typically installed when the container builds (via `pip install .` in `Dockerfile`). If you manually change `pyproject.toml`, you might need to reinstall:
        ```bash
        pip install -e .
        ```
    *   Frontend dependencies: After cloning for the first time, or pulling new changes that affect `package.json` or `frontend/package.json`, ensure Node.js packages are installed by running the following commands from the project root:
        ```bash
        npm install
        npm install --prefix frontend
        ```
5.  Once the container is running and dependencies are set, the application will be available. See the "Accessing the Application" section below.


### Frontend Development Workflow (inside Dev Container)

This project uses Tailwind CSS for styling and React (with Vite) for building modern user interface components.

*   **Building Frontend Assets**:
    *   To compile Tailwind CSS and build the React application (outputting to `meal_planner_app/static/`), run the following command from the project root:
        ```bash
        npm run build
        ```
    *   This command is automatically executed when the Docker image is built, so frontend assets are typically up-to-date within the dev container. Run it manually if you make changes to frontend source files and want to produce a static build without using the Vite dev server.

*   **React Development Server (for UI development with Hot Reloading)**:
    *   For a faster development experience when working on React components, you can use the Vite development server. From the project root, run:
        ```bash
        npm --prefix frontend run dev
        ```
    *   This will typically start a server on `http://localhost:5173` (check your terminal output). It provides Hot Module Replacement (HMR) for immediate feedback on UI changes made in the `frontend/src` directory.
    *   **Note**: The main Flask application (including backend APIs) still runs on `http://localhost:5000` (or as configured in the `Dockerfile`). The React development server is specifically for frontend component development. API calls from the React app are configured in `frontend/vite.config.js` (if proxying) or made directly to the Flask server's address (e.g., `fetch('/api/recipes')` will target `http://localhost:5000/api/recipes` when the React app runs on `localhost:5173` due to browser same-origin policy for relative paths, or if Vite proxy is set up).

## Accessing the Application

*   The main Flask application (with traditional Jinja2 templates) is available at: `http://localhost:5000`
*   The new UI being developed with React is available at: `http://localhost:5000/ui/`

## Implemented Features

- Create, Read, Update, and Delete Recipes (via Jinja2 templates and supporting API)
- Create, Read, Update, and Delete Meal Plans (via Jinja2 templates)
- Generate Shopping Lists from Meal Plans (via Jinja2 templates)
- Basic React frontend for displaying recipes (accessible at `/ui/`)
- API endpoint `/api/recipes` to serve recipe data as JSON.

# Meal planning tool that supports:
(This section describes the overall goals, some of which are covered by Implemented Features)
1. Storing meal recipies, broken down to ingredients with links to their origin
2. Searching for new recipies based on a set of preferences (ingredients, taste, meal type, quisine)
3. Manual preparation of the list of meals and generating the list of all needed ingredients
4. Exporting to pdf
