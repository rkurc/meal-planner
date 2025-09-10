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

## Getting Started (Manual Setup)

This guide is for setting up the development environment manually, without using the provided Dev Container.

### Prerequisites

*   Python 3.11+
*   Node.js 18+ and npm

### Backend Setup

1.  **Navigate to the project root directory.**

2.  **Create and activate a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # .\\venv\\Scripts\\activate  # On Windows
    ```

3.  **Install Python dependencies:**
    The project uses `pyproject.toml` to manage dependencies. Install them using pip:
    ```bash
    pip install -e .[dev]
    ```

4.  **Run the backend server:**
    The Flask server provides the API for the application.
    ```bash
    python -m meal_planner_app.main
    ```
    The backend will be running at `http://127.0.0.1:5000`.

5.  **Run backend tests:**
    The project uses pytest for unit testing.
    ```bash
    pytest
    ```

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Run the frontend development server:**
    This server provides hot-reloading for a better development experience.
    ```bash
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173`. The Vite server is configured to proxy API requests to the backend on port 5000.

4.  **Build frontend for production:**
    This command compiles the frontend assets into the `meal_planner_app/static/react_app` directory, which allows the Flask app to serve them directly.
    ```bash
    npm run build
    ```

# Meal planning tool that supports:
(This section describes the overall goals, some of which are covered by Implemented Features)
1. Storing meal recipies, broken down to ingredients with links to their origin
2. Searching for new recipies based on a set of preferences (ingredients, taste, meal type, quisine)
3. Manual preparation of the list of meals and generating the list of all needed ingredients
4. Exporting to pdf
