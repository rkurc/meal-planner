# System Requirements

Functional and non-functional requirements for the Meal Planning Tool. **Status notes reconciled 2026-09-02** (see `.ai/progress.md`).

## 1. Functional Requirements

### 1.1 Automatic Recipe Discovery *(NOT IMPLEMENTED — FUTURE)*

**Status (2026-09-02):** No implementation, UI, backend, or scraping/NLP dependencies. FRs below remain aspirational. Test cases TC-ARD-* stay future.

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

### 1.2 Recipe Management *(MOSTLY IMPLEMENTED — metadata gap)*

**Status:** CRUD for name, description, instructions, source URL, and ingredients is implemented (API + React). Jinja recipe pages are decommissioned. **FR-1.2.1 is only partially met:** the `Recipe` model has **no** declared preparation time, actual preparation time, or shelf life.

*   **FR-1.2.1:** The system shall allow a user to create a new recipe, providing fields for: a recipe name, preparation instructions, the recipe's source URL, the declared preparation time, the actual preparation time, and the dish's shelf life. *(Partial — times and shelf life missing.)*
*   **FR-1.2.2:** The system shall allow a user to associate a list of ingredients with a recipe, using the flexible unit system defined in Ingredient Management. *(Met.)*
*   **FR-1.2.3:** The system shall display a list of all saved recipes. *(Met.)*
*   **FR-1.2.4:** The system shall allow a user to view the full details of a single recipe, including all its metadata and ingredients. *(Met for stored fields.)*
*   **FR-1.2.5:** The system shall allow a user to edit the details of an existing recipe. *(Met.)*
*   **FR-1.2.6:** The system shall allow a user to delete a recipe from the system. *(Met.)*
*   **FR-1.2.7:** The system shall provide an API endpoint (`/api/recipes`) that returns a list of all recipes in JSON format. *(Met; also POST/PUT/DELETE; list accepts `q` and `ingredient` filters.)*

### 1.3 Ingredient Management *(PARTIAL)*

**Status:** FR-1.3.4 is met on **embedded** recipe ingredients. FR-1.3.2 is **partially** met by a read-only aggregation list (`GET /api/ingredients/summary` + `/ui/ingredients`). FR-1.3.1 and FR-1.3.3 are **not** met (no master create/edit/delete; "Add new ingredient" opens the recipe form). `/api/ingredients` exists but returns unique **name strings** for autocomplete, not a master resource.

*   **FR-1.3.1:** The system shall allow a user to create a new ingredient with a unique name. *(Not met as a master entity.)*
*   **FR-1.3.2:** The system shall allow a user to view a list of all available ingredients. *(Partial — names currently used in recipes only.)*
*   **FR-1.3.3:** The system shall allow a user to edit or delete an existing ingredient. *(Not met. `IngredientDetail.jsx` is unrouted dead code.)*
*   **FR-1.3.4:** The system shall support a flexible data model for ingredient measurements, capturing a numeric amount and a unit string which can represent quantity, weight (e.g., "g", "kg"), volume (e.g., "ml", "cup"), or packaging (e.g., "can", "package"). *(Met.)*

### 1.4 Meal Plan Management *(IMPLEMENTED — no calendar)*

**Status:** CRUD + recipe membership + counts/multipliers in API and React. FR-1.4.1 "date range" is **not** modeled (name + description only). Jinja meal-plan pages are decommissioned.

*   **FR-1.4.1:** The system shall allow a user to create a new meal plan, specifying a name or date range for the plan. *(Name yes; date range no.)*
*   **FR-1.4.2:** The system shall allow a user to add recipes from the recipe collection to a meal plan. *(Met; React also sets a count.)*
*   **FR-1.4.3:** The system shall display the details of a meal plan. *(Met.)*
*   **FR-1.4.4:** The system shall allow a user to edit or delete a meal plan. *(Met.)*

### 1.5 Shopping List Generation *(IMPLEMENTED in API + React)*

**Status:** Generation, consolidation, persistence, manual edit, standalone lists, delete, and PDF of the **persisted** list are implemented. Jinja on-the-fly HTML shopping table is decommissioned; meal-plan PDF route remains.

*   **FR-1.5.1:** The system shall automatically generate a shopping list based on a selected meal plan. *(Met. Quantities multiply by meal-plan recipe count.)*
*   **FR-1.5.2:** The system shall consolidate ingredients from multiple recipes. Consolidation should only occur for identical ingredients with compatible units (e.g., 'g' with 'kg', 'cup' with 'cup'). The system should not attempt to consolidate incompatible units (e.g., 'cups' with 'grams' without a conversion table, or 'apples' with 'grams'). *(Met for **same unit string** + name + location. There is still **no g↔kg conversion table** — 100g and 0.2kg stay separate unless units match.)*
*   **FR-1.5.3:** The system shall display the generated shopping list to the user. *(Met.)*
*   **FR-1.5.4:** The system shall allow the user to manually add, edit, or remove items from the generated shopping list. *(Met in React + API.)*

### 1.6 User Interface

*   **FR-1.6.1:** The system shall provide a web-based user interface accessible through a browser. *(Met.)*
*   **FR-1.6.2:** The traditional interface (Jinja2) shall provide access to all defined features. *(Withdrawn — Jinja HTML UI decommissioned 2026-09-02. `GET /` 302 → `/ui/`; other HTML GETs 302 to `/ui/…`.)*
*   **FR-1.6.3:** The modern interface (React @ `/ui/`) shall provide, at a minimum, the ability to display recipes. *(Exceeded: recipes including search, meal plans, shopping lists, ingredient list. This is the only HTML UI.)*

### 1.7 Future/Desired Features

*   **FR-1.7.1:** The system should provide an advanced search functionality to filter locally stored recipes. *(Met: `crud.search_recipes` via `GET /api/recipes?q=&ingredient=` and React `RecipeList`.)*
*   **FR-1.7.2:** The system should allow exporting a shopping list or meal plan to a PDF document. *(Shopping list PDF: Done from React (persisted) and meal-plan generated PDF route. Meal-plan-as-PDF document: not implemented.)*

## 2. Non-Functional Requirements

### 2.1 Performance
*   **NFR-2.1.1:** Web pages should load in a user's browser in under 3 seconds on a standard broadband connection. *(Not formally measured.)*
*   **NFR-2.1.2:** Recipe search/extraction from a given URL should complete within 15 seconds. *(Future — no discovery.)*
*   **NFR-2.1.3:** The `/api/recipes` endpoint should respond with data in under 500ms for up to 1000 recipes. *(Plausible for in-memory; not load-tested.)*

### 2.2 Usability
*   **NFR-2.2.1:** The user interface should be intuitive and require minimal training.
*   **NFR-2.2.2:** The system should provide clear feedback to the user during the recipe extraction process (e.g., "Crawling page...", "Extracting ingredients...", "Success!"). *(Future — discovery only.)*

### 2.3 Reliability
*   **NFR-2.3.1:** The application should be available and operational 99.9% of the time. *(Not measured; in-memory store is process-local.)*
*   **NFR-2.3.2:** The system should handle common user errors gracefully (e.g., invalid URL, non-recipe webpage). *(CRUD paths have basic 4xx; discovery errors are future.)*

### 2.4 Maintainability
*   **NFR-2.4.1:** The codebase should be well-documented. *(`.ai/` + README; this pass re-aligned them after Jinja decommission.)*
*   **NFR-2.4.2:** The project should follow a consistent coding style. *(pre-commit: black + pylint; prettier + eslint.)*
*   **NFR-2.4.3:** The AI/extraction logic should be modular and separable from the core application logic. *(Future.)*

### 2.5 AI/Extraction Accuracy
*   **NFR-2.5.1:** The AI extraction process shall correctly identify and extract ingredients and their quantities with at least 90% accuracy on a benchmark set of common recipe websites. *(Future.)*
