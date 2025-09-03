# System Requirements

This document outlines the functional and non-functional requirements for the Meal Planning Tool. These are derived from the feature summary and an analysis of the project's goals.

## 1. Functional Requirements

Functional requirements define the specific behaviors and functions of the system.

### 1.1 Automatic Recipe Discovery

#### 1.1.1 Search-Based Discovery
*   **FR-1.1.1.1:** The system shall provide an interface for the user to input a search query, such as a list of ingredients or a type of dish.
*   **FR-1.1.1.2:** The system shall use the user's query to search the web for relevant recipe pages.
*   **FR-1.1.1.3:** The system shall display a list of search results (e.g., titles and links) to the user.
*   **FR-1.1.1.4:** The system shall allow the user to select a search result to initiate the extraction process described in the next section.

#### 1.1.2 URL-Based Extraction
*   **FR-1.1.2.1:** The system shall provide an interface for the user to submit a single URL pointing to a recipe page.
*   **FR-1.1.2.2:** The system shall crawl the provided webpage to retrieve its content.
*   **FR-1.1.2.3:** The system shall use an intelligent/AI-driven process to parse the webpage content and extract key recipe information (e.g., name, instructions, ingredients, quantities, units).
*   **FR-1.1.2.4:** The system shall present the extracted information to the user for review and confirmation, potentially by pre-filling the standard "Add Recipe" form.

### 1.2 Recipe Management

*   **FR-1.2.1:** The system shall allow a user to create a new recipe, providing fields for: a recipe name, preparation instructions, the recipe's source URL, the declared preparation time, the actual preparation time, and the dish's shelf life.
*   **FR-1.2.2:** The system shall allow a user to associate a list of ingredients with a recipe, using the flexible unit system defined in Ingredient Management.
*   **FR-1.2.3:** The system shall display a list of all saved recipes.
*   **FR-1.2.4:** The system shall allow a user to view the full details of a single recipe, including all its metadata and ingredients.
*   **FR-1.2.5:** The system shall allow a user to edit the details of an existing recipe.
*   **FR-1.2.6:** The system shall allow a user to delete a recipe from the system.
*   **FR-1.2.7:** The system shall provide an API endpoint (`/api/recipes`) that returns a list of all recipes in JSON format.

### 1.3 Ingredient Management

*   **FR-1.3.1:** The system shall allow a user to create a new ingredient with a unique name.
*   **FR-1.3.2:** The system shall allow a user to view a list of all available ingredients.
*   **FR-1.3.3:** The system shall allow a user to edit or delete an existing ingredient.
*   **FR-1.3.4:** The system shall support a flexible data model for ingredient measurements, capturing a numeric amount and a unit string which can represent quantity, weight (e.g., "g", "kg"), volume (e.g., "ml", "cup"), or packaging (e.g., "can", "package").

### 1.4 Meal Plan Management

*   **FR-1.4.1:** The system shall allow a user to create a new meal plan, specifying a name or date range for the plan.
*   **FR-1.4.2:** The system shall allow a user to add recipes from the recipe collection to a meal plan.
*   **FR-1.4.3:** The system shall display the details of a meal plan.
*   **FR-1.4.4:** The system shall allow a user to edit or delete a meal plan.

### 1.5 Shopping List Generation

*   **FR-1.5.1:** The system shall automatically generate a shopping list based on a selected meal plan.
*   **FR-1.5.2:** The system shall consolidate ingredients from multiple recipes. Consolidation should only occur for identical ingredients with compatible units (e.g., 'g' with 'kg', 'cup' with 'cup'). The system should not attempt to consolidate incompatible units (e.g., 'cups' with 'grams' without a conversion table, or 'apples' with 'grams').
*   **FR-1.5.3:** The system shall display the generated shopping list to the user.
*   **FR-1.5.4:** The system shall allow the user to manually add, edit, or remove items from the generated shopping list.

### 1.6 User Interface

*   **FR-1.6.1:** The system shall provide a web-based user interface accessible through a browser.
*   **FR-1.6.2:** The traditional interface (Jinja2) shall provide access to all defined features.
*   **FR-1.6.3:** The modern interface (React @ `/ui/`) shall provide, at a minimum, the ability to display recipes.

### 1.7 Future/Desired Features

*   **FR-1.7.1:** The system should provide an advanced search functionality to filter locally stored recipes.
*   **FR-1.7.2:** The system should allow exporting a shopping list or meal plan to a PDF document.

## 2. Non-Functional Requirements

Non-functional requirements define the quality attributes and constraints of the system.

### 2.1 Performance
*   **NFR-2.1.1:** Web pages should load in a user's browser in under 3 seconds on a standard broadband connection.
*   **NFR-2.1.2:** Recipe search/extraction from a given URL should complete within 15 seconds.
*   **NFR-2.1.3:** The `/api/recipes` endpoint should respond with data in under 500ms for up to 1000 recipes.

### 2.2 Usability
*   **NFR-2.2.1:** The user interface should be intuitive and require minimal training.
*   **NFR-2.2.2:** The system should provide clear feedback to the user during the recipe extraction process (e.g., "Crawling page...", "Extracting ingredients...", "Success!").

### 2.3 Reliability
*   **NFR-2.3.1:** The application should be available and operational 99.9% of the time.
*   **NFR-2.3.2:** The system should handle common user errors gracefully (e.g., invalid URL, non-recipe webpage).

### 2.4 Maintainability
*   **NFR-2.4.1:** The codebase should be well-documented.
*   **NFR-2.4.2:** The project should follow a consistent coding style.
*   **NFR-2.4.3:** The AI/extraction logic should be modular and separable from the core application logic to allow for independent updates and improvements.

### 2.5 AI/Extraction Accuracy
*   **NFR-2.5.1:** The AI extraction process shall correctly identify and extract ingredients and their quantities with at least 90% accuracy on a benchmark set of common recipe websites.
