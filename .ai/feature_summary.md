# Feature Summary

This document outlines the major features of the Meal Planning Tool, based on the information provided in the `README.md` file and subsequent user feedback.

## High-Level Summary

*   **Automatic Recipe Discovery:** *(NOT YET IMPLEMENTED)* Planned: automatically find and import recipes from the web (search-based discovery + direct URL extraction). No code or UI exists yet.
*   **Ingredient Management:** *(PARTIAL - embedded only)* Ingredients support flexible units, but there is no centralized standalone master list or CRUD. Ingredients are managed only as part of recipes.
*   **Recipe Management:** The application allows users to create, read, update, and delete meal recipes with detailed metadata. **Implemented** in both legacy Jinja2 and full React UI + complete API.
*   **Meal Plan Management:** Users can create, read, update, and delete weekly or daily meal plans. **Implemented** fully (API + React + legacy).
*   **Shopping List Generation:** The system can automatically generate a shopping list from a meal plan (with consolidation), which can then be manually adjusted and persisted. **Implemented** (API + React view + legacy + PDF in legacy).
*   **Modern UI:** React SPA (using Vite/Tailwind) provides full feature parity for recipes, meal plans, and shopping lists. Accessible at `/static/react_app/`. Legacy Jinja2 UI remains available and complete.
*   **API:** Full REST API for recipes, meal-plans (incl. associations and shopping gen), and persistent shopping-lists. (No auth yet.)

## Detailed Feature Descriptions

### Automatic Recipe Discovery *(NOT YET IMPLEMENTED)*
**Status (as of 2026-06-16):** This is a planned/future feature. Zero implementation exists. No web search, scraping, BeautifulSoup, spacy, or URL extraction logic in Python or JS sources (verified).

This *would be* a powerful feature for populating the recipe database with minimal manual entry. It would operate in two modes:
1.  **Search-Based Discovery:** Users can provide a list of ingredients or a type of dish (e.g., "vegan pasta"). The system then searches the web for matching recipes and presents a list of potential candidates for the user to import.
2.  **URL-Based Extraction:** If a user has already found a recipe they like, they can provide the URL directly. The system will then crawl that specific page, extract all relevant information (ingredients, instructions, etc.) using an intelligent, possibly AI-supported, process, and add it to the recipe database (or pre-fill the Add form for review).

### Ingredient Management *(NO STANDALONE MASTER LIST - EMBEDDED ONLY)*
**Status:** No dedicated ingredient management UI or API (FR-1.3 / TC-ING-* are future). Ingredients support flexible units of measure but only exist embedded inside recipes.

The application supports flexible measurement units when defining ingredients *as part of recipes*. An ingredient can be defined by:
*   **Quantity:** e.g., "2 apples"
*   **Weight:** e.g., "250g of flour"
*   **Volume:** e.g., "1 cup of milk"
*   **Packaging:** e.g., "1 can of tomatoes"
This flexibility is used for recipe storage, consolidation in shopping lists, and legacy form parsing. A centralized "master list of ingredients" CRUD is not implemented.

### Recipe Management
The core of the application is the ability to manage a collection of recipes. In addition to standard CRUD operations, recipes can store rich metadata:
*   A list of ingredients with their flexible quantities and units.
*   The source of the recipe (e.g., a URL).
*   The preparation time as declared in the recipe source.
*   The actual time it takes to prepare the dish, based on user experience.
*   The shelf life of the final dish (i.e., for how long it is edible).

**Implementation status:** Fully implemented in legacy Jinja2 UI, React UI (RecipeList/Detail/Form), and complete API. (No longer "primarily Jinja2".)

### Meal Plan Management
Users can organize recipes into meal plans. This feature allows for the creation of daily or weekly meal schedules.

**Implementation status:** Full CRUD + recipe add/remove + shopping generation in API, React (MealPlan* components), and legacy.

### Shopping List Generation
A key utility of the application is its ability to simplify grocery shopping. After a user creates a meal plan, the application can process all the recipes in that plan and generate a consolidated shopping list. A crucial part of this feature is the ability for the user to **manually edit the list after generation**. The system must also be able to intelligently handle the consolidation of flexible units where possible.

**Implementation status:** Fully implemented:
- Generation + consolidation logic in backend.
- Persistent storage + CRUD via `/api/shopping-lists`.
- View/edit in React `ShoppingListView` (and legacy).
- PDF export available via legacy route.

### Modern User Interface (React Frontend)
The project includes a full-featured modern frontend built with React (v18), React Router, Axios, Vite, and Tailwind. Accessible at the `/static/react_app/` (routed under basename) or proxied `/ui/`.

**Current coverage:** Recipes (full CRUD), Meal Plans (full), Shopping lists (view + edit). Uses the complete API. E2E tests cover key flows. (Legacy Jinja2 UI coexists.)

### APIs
The application exposes a full RESTful JSON API:
- `/api/recipes` + per-ID (full CRUD)
- `/api/meal-plans` + associations + shopping gen (full)
- `/api/shopping-lists` (full persistent CRUD)

API is unauthenticated at present.

### Future Goals / Desired Features
The documentation also outlines several long-term goals for the application:
*   **Advanced Recipe Search:** A powerful search function to find recipes stored locally based on specific criteria. *(Not implemented in React; basic legacy support only.)*
*   **PDF Export:** The ability to export meal plans or shopping lists to a PDF file for easy printing or sharing. *(Implemented in legacy Jinja only; not first-class from React yet.)*
*   **Automatic Recipe Discovery and Standalone Ingredients:** Major planned features (marked not implemented above).
