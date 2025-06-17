# Meal Planner App MVP

## Description

This is a simple Flask-based web application for managing recipes and meal plans. It allows users to perform CRUD (Create, Read, Update, Delete) operations on recipes, organize them into meal plans, generate shopping lists for those plans, and export shopping lists to PDF. It also features a basic search for recipes by name, description, or ingredients.

The application uses in-memory data storage, meaning data will be lost when the server restarts.

## Prerequisites

*   Python 3.7+
*   pip (Python package installer)

## Setup Instructions

1.  **Clone the repository (if applicable) or ensure you have the project files.**

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    Navigate to the `meal_planner_app` directory (where `requirements.txt` is located if it's inside, or the root if `requirements.txt` is at the root - current setup has `requirements.txt` at the root of what the agent sees, which is effectively the parent of `meal_planner_app` directory if we consider the full structure, but for a user, they'd likely have `requirements.txt` in their project root). Assuming `requirements.txt` is in the same directory as this `README.md` (which should be project root).

    ```bash
    pip install -r requirements.txt
    ```
    (Note: The `requirements.txt` is in the parent directory of `meal_planner_app/` based on current structure. If this README is in `meal_planner_app/`, then `pip install -r ../requirements.txt` might be needed, or `requirements.txt` should be moved here. For a typical project, `requirements.txt` is at the root.)

    *Correction based on current project structure: `requirements.txt` is at the root level, one level above the `meal_planner_app` directory where `main.py` resides.*
    If running from the directory containing `meal_planner_app/` and `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask development server:**
    Ensure your current directory is the one containing `requirements.txt` and the `meal_planner_app` folder.
    ```bash
    python -m meal_planner_app.main
    ```
    Or, if you set `FLASK_APP` environment variable:
    ```bash
    export FLASK_APP=meal_planner_app.main  # On macOS/Linux
    # set FLASK_APP=meal_planner_app.main    # On Windows
    flask run
    ```
    The application should be accessible at `http://127.0.0.1:5000/` in your web browser.

## Features

*   **Recipe Management:**
    *   Create, view, edit, and delete recipes.
    *   Recipes include name, description, ingredients (name, quantity, unit), instructions, and source URL.
*   **Meal Plan Creation:**
    *   Create named meal plans.
    *   Add/remove recipes to/from meal plans.
    *   View recipes within a meal plan.
    *   Rename and delete meal plans.
*   **Shopping List Generation:**
    *   Generate an aggregated shopping list for all recipes in a meal plan.
    *   Handles numeric quantity summation and lists non-numeric quantities.
    *   Export shopping list to PDF.
*   **Recipe Search:**
    *   Search recipes by name, description, or ingredient names.

## Project Structure
```
.
├── meal_planner_app/
│   ├── __init__.py
│   ├── crud.py         # Data manipulation logic
│   ├── main.py         # Flask app, routes
│   ├── models/         # Data models (Recipe, Ingredient, MealPlan)
│   │   ├── __init__.py
│   │   ├── ingredient.py
│   │   ├── meal_plan.py
│   │   └── recipe.py
│   ├── services.py     # Other services (e.g., PDF generation)
│   ├── static/         # (Optional, for CSS/JS if added)
│   ├── templates/      # HTML templates
│   └── tests/          # Unit tests
│       ├── __init__.py
│       ├── test_crud.py
│       └── test_shopping_list.py
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

(Assuming this `README.md` will be placed in the root, alongside `requirements.txt` and the `meal_planner_app` directory itself).The `README.md` has been created. I've made an assumption about its final location (project root) for the setup instructions to make sense.

Step 3: UI/UX Refinements (Conceptual List)
Here are 3-5 potential UI/UX improvements:

1.  **Advanced Ingredient Input in Forms:** Instead of a simple textarea for ingredients, use a dynamic form section where users can add ingredients one by one with separate fields for name, quantity, and unit. Autocomplete suggestions for ingredient names and units could be added. This would make data entry more structured and reduce parsing errors.
2.  **AJAX for List Management:** When adding or removing recipes from a meal plan, or ingredients from a recipe (if that level of detail were added), use AJAX requests. This would update the relevant list on the page without a full page reload, providing a smoother and faster user experience.
3.  **Interactive Meal Calendar View:** For meal plans, instead of just a list of recipes, a visual calendar (e.g., weekly or monthly view) could be implemented where recipes can be dragged and dropped onto specific days or meal slots (breakfast, lunch, dinner).
4.  **User Feedback and Notifications:** Implement more user-friendly feedback, such as "toast" notifications for actions like "Recipe saved successfully" or "Meal plan deleted." Currently, feedback is mostly through page reloads showing the new state.
5.  **Improved Visual Styling & Responsiveness:** Apply a lightweight CSS framework (like Bootstrap, Tailwind CSS, or even a simpler one like Pico.css) to improve the overall look and feel, and ensure the application is responsive and usable on different screen sizes.

Step 4: Deployment Options (Conceptual List)
Here are 2-3 common deployment options:

1.  **PythonAnywhere:** A PaaS (Platform as a Service) that is very beginner-friendly for Python web apps. It simplifies deployment by handling server configuration, WSGI setup, and provides a web-based interface for management. Good for small to medium Flask apps.
2.  **Heroku:** Another popular PaaS. While its free tiers have become more limited, it's still a viable option for deploying Flask apps. Requires a `Procfile` to define how the app runs (e.g., using Gunicorn). Git integration makes deployment straightforward.
3.  **Docker on a Cloud VM (e.g., AWS EC2, Google Cloud Compute Engine, Azure VM):**
    *   Containerize the Flask application using Docker (with a `Dockerfile`). This packages the app and its dependencies.
    *   Run the container on a cloud virtual machine.
    *   Use a production-grade WSGI server like Gunicorn inside the container.
    *   Optionally, set up a reverse proxy like Nginx in front of Gunicorn for handling static files, SSL termination, and request buffering. This offers more control and scalability but involves more setup.
    *   Managed container services like Google Cloud Run or AWS Fargate can also run Docker containers with less VM management.

Step 5: Stretch Goal: Advanced Search Filter - Filter by Ingredient Presence.
I will now proceed to implement this. First, modifying `crud.py`.
