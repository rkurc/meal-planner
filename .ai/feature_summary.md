# Feature Summary

This document outlines the major features of the Meal Planning Tool, based on the information provided in the `README.md` file and subsequent user feedback.

## High-Level Summary

*   **Automatic Recipe Discovery:** The application can automatically find and import recipes from the web using two different modes: a search-based discovery and a direct URL extraction.
*   **Ingredient Management:** The application provides a centralized place to manage ingredients, supporting flexible units of measure (e.g., quantity, weight, package).
*   **Recipe Management:** The application allows users to create, read, update, and delete meal recipes with detailed metadata.
*   **Meal Plan Management:** Users can create, read, update, and delete weekly or daily meal plans.
*   **Shopping List Generation:** The system can automatically generate a shopping list from a meal plan, which can then be manually adjusted.
*   **Modern UI (In-Progress):** A new user interface is being developed using React to provide a more modern user experience for some features.
*   **API for Recipes:** A JSON API is available to fetch recipe data, allowing for decoupling the frontend from the backend.

## Detailed Feature Descriptions

### Automatic Recipe Discovery
This is a powerful feature for populating the recipe database with minimal manual entry. It operates in two modes:
1.  **Search-Based Discovery:** Users can provide a list of ingredients or a type of dish (e.g., "vegan pasta"). The system then searches the web for matching recipes and presents a list of potential candidates for the user to import.
2.  **URL-Based Extraction:** If a user has already found a recipe they like, they can provide the URL directly. The system will then crawl that specific page, extract all relevant information (ingredients, instructions, etc.) using an intelligent, possibly AI-supported, process, and add it to the recipe database.

### Ingredient Management
The application allows for the management of a master list of ingredients. A key aspect of this feature is the support for **flexible measurement units**. This means an ingredient in a recipe is not tied to a single unit type. It can be defined by:
*   **Quantity:** e.g., "2 apples"
*   **Weight:** e.g., "250g of flour"
*   **Volume:** e.g., "1 cup of milk"
*   **Packaging:** e.g., "1 can of tomatoes"
This flexibility is crucial for accurately importing recipes and for generating useful shopping lists.

### Recipe Management
The core of the application is the ability to manage a collection of recipes. In addition to standard CRUD operations, recipes can store rich metadata:
*   A list of ingredients with their flexible quantities and units.
*   The source of the recipe (e.g., a URL).
*   The preparation time as declared in the recipe source.
*   The actual time it takes to prepare the dish, based on user experience.
*   The shelf life of the final dish (i.e., for how long it is edible).

This feature is primarily implemented using server-rendered Jinja2 templates.

### Meal Plan Management
Users can organize recipes into meal plans. This feature allows for the creation of daily or weekly meal schedules.

### Shopping List Generation
A key utility of the application is its ability to simplify grocery shopping. After a user creates a meal plan, the application can process all the recipes in that plan and generate a consolidated shopping list. A crucial part of this feature is the ability for the user to **manually edit the list after generation**. The system must also be ableto intelligently handle the consolidation of flexible units where possible.

### Modern User Interface (React Frontend)
The project includes a newer, more modern frontend built with React, accessible at the `/ui/` endpoint.

### Recipe API
The application exposes a RESTful API endpoint at `/api/recipes` to serve recipe data in JSON format.

### Future Goals / Desired Features
The documentation also outlines several long-term goals for the application:
*   **Advanced Recipe Search:** A powerful search function to find recipes stored locally based on specific criteria.
*   **PDF Export:** The ability to export meal plans or shopping lists to a PDF file for easy printing or sharing.
