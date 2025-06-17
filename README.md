## Development Environment

This project includes a Dev Container configuration, making it easy to get started with local development.

### Prerequisites

- Docker Desktop
- Visual Studio Code
- Remote - Containers (VS Code Extension)

### Getting Started

1. Clone the repository.
2. Open the repository in Visual Studio Code.
3. When prompted, click "Reopen in Container". This will build the Docker image and start the Dev Container.
4. Once the container is running, the application will be available at http://localhost:5000.

## Implemented Features

- Create, Read, Update, and Delete Recipes
- Create, Read, Update, and Delete Meal Plans
- Generate Shopping Lists from Meal Plans

# Meal planning tool that supports:
1. Storing meal recipies, broken down to ingredients with links to their origin
2. Searching for new recipies based on a set of preferences (ingredients, taste, meal type, quisine)
3. Manual preparation of the list of meals and generating the list of all needed ingredients
4. Exporting to pdf
