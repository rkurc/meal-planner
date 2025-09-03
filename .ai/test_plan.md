# Detailed Test Plan

## 1. Introduction

This document outlines the test plan for the Meal Planner application. Its purpose is to provide a comprehensive strategy for verifying the functionality, reliability, and performance of the system. This plan is based on the features and requirements defined in `feature_summary.md` and `requirements.md`.

## 2. Scope

### 2.1 In Scope

*   Testing of all defined features, including Automatic Recipe Discovery, Recipe/Ingredient Management, Meal Plan Management, and Shopping List Generation.
*   Verification of both the traditional Jinja2-based UI and the modern React-based UI.
*   Testing of the `/api/recipes` API endpoint.
*   Validation of all non-functional requirements, including performance and AI accuracy.

### 2.2 Out of Scope

*   This document does not include the *implementation* of the tests, only the plan.
*   Testing of third-party dependencies (e.g., the Flask framework itself) is not in scope.

## 3. Test Strategy

A multi-layered testing approach will be used:

*   **Unit Tests:** To test individual functions and components in isolation. `pytest` for the backend and React Testing Library/Jest for the frontend are recommended.
*   **Integration Tests:** To test the interaction between components, such as the interaction between the Flask routes and the database logic.
*   **API Tests:** To directly test the `/api/recipes` endpoint for correctness, error handling, and performance. Tools like `Postman` or `pytest` with an HTTP client can be used.
*   **End-to-End (E2E) Tests:** To simulate real user workflows in a browser. This is critical for testing both the Jinja2 and React UIs. Tools like `Playwright` or `Cypress` are recommended.
*   **Manual Testing:** For exploratory testing and validating usability requirements that are difficult to automate.

## 4. Test Cases

### 4.1 Automatic Recipe Discovery

#### 4.1.1 Search-Based Discovery
| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type |
|---|---|---|---|---|---|
| **TC-ARD-S-001** | FR-1.1.1.1, FR-1.1.1.2 | Verify user can search for recipes by dish type. | 1. Navigate to "Discover Recipes".<br>2. Enter "chicken pasta" into the search field.<br>3. Submit the search. | The system displays a list of links to recipes related to "chicken pasta". | E2E |
| **TC-ARD-S-002** | FR-1.1.1.3, FR-1.1.1.4 | Verify user can select a search result for extraction. | 1. Perform a search.<br>2. Click the "Import" or "Extract" button next to a valid search result. | The system proceeds to the URL-based extraction workflow for the selected link. | E2E |

#### 4.1.2 URL-Based Extraction
| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type |
|---|---|---|---|---|---|
| **TC-ARD-U-001** | FR-1.1.2.1, FR-1.1.2.2 | Verify user can submit a URL for extraction. | 1. Navigate to "Import from URL".<br>2. Enter a valid recipe URL.<br>3. Click "Extract". | The system shows a loading/progress indicator and begins the extraction process. | E2E |
| **TC-ARD-U-002** | FR-1.1.2.3, FR-1.1.2.4 | Verify recipe data is extracted and presented for confirmation. | 1. Submit a valid URL for extraction. | The "Add Recipe" form is displayed, pre-filled with the extracted name, instructions, and ingredients for user review. | Integration |
| **TC-ARD-U-003** | NFR-2.3.2 | Verify system handles a non-recipe URL gracefully. | 1. Submit a URL that is not a recipe (e.g., google.com). | The system displays a user-friendly error message, such as "Could not find a recipe at the provided URL." | E2E |

### 4.2 Recipe Management

| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type |
|---|---|---|---|---|---|
| **TC-REC-001** | FR-1.2.1, FR-1.2.2 | Verify user can create a recipe with all metadata. | 1. Navigate to "Add Recipe".<br>2. Fill in all fields, including times and shelf-life.<br>3. Submit. | The new recipe is created and visible in the recipe list. | E2E |
| **TC-REC-002** | FR-1.2.3, FR-1.2.4 | Verify recipe list and detail pages display correctly. | 1. Navigate to the recipe list.<br>2. Click on a recipe. | All recipes are listed. The detail page shows all saved metadata correctly. | E2E |
| **TC-REC-003** | FR-1.2.5 | Verify a user can edit an existing recipe. | 1. Navigate to a recipe's detail page.<br>2. Click "Edit" and change a field.<br>3. Submit. | The recipe's details are updated with the new information. | E2E |
| **TC-REC-004** | FR-1.2.6 | Verify a user can delete a recipe. | 1. Navigate to a recipe's detail page.<br>2. Click "Delete" and confirm. | The recipe is removed from the recipe list. | E2E |
| **TC-REC-005** | FR-1.2.7 | Verify the `/api/recipes` endpoint returns a list of recipes. | 1. Send a GET request to `/api/recipes`. | The API returns a `200 OK` status with a JSON array of recipe objects. | API |
| **TC-REC-006** | FR-1.6.3 | Verify that recipes are displayed on the React UI. | 1. Navigate to the `/ui/` page. | The page loads and displays a list of recipes fetched from the API. | E2E |
| **TC-REC-007** | FR-1.3.4 | Verify recipe can be created with flexible ingredient units. | 1. Create a recipe.<br>2. Add an ingredient with quantity "250" and unit "g".<br>3. Add another with "1" and "can".<br>4. Save. | The recipe saves and displays the ingredients with their correct flexible units. | E2E |

### 4.3 Ingredient Management

| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type |
|---|---|---|---|---|---|
| **TC-ING-001** | FR-1.3.1 | Verify a user can create a new ingredient. | 1. Navigate to "Manage Ingredients".<br>2. Click "Add Ingredient", enter a name, and save. | The new ingredient appears in the master list. | E2E |
| **TC-ING-002** | FR-1.3.2 | Verify the ingredient list page displays all items. | 1. Navigate to "Manage Ingredients". | All created ingredients are displayed. | E2E |
| **TC-ING-003** | FR-1.3.3 | Verify a user can edit or delete an ingredient. | 1. From the ingredient list, edit or delete an item. | The ingredient is updated or removed from the list. | E2E |

### 4.4 Meal Plan Management

| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type |
|---|---|---|---|---|---|
| **TC-MP-001** | FR-1.4.1, FR-1.4.2 | Verify a user can create a meal plan and add recipes. | 1. Navigate to "Create Meal Plan".<br>2. Name the plan, add recipes, and save. | The new meal plan is created and displayed, showing the selected recipes. | E2E |
| **TC-MP-002** | FR-1.4.4 | Verify that a user can edit or delete a meal plan. | 1. From the meal plan list, edit or delete a plan. | The plan is updated or removed from the list. | E2E |

### 4.5 Shopping List Generation

| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type |
|---|---|---|---|---|---|
| **TC-SL-001** | FR-1.5.1, FR-1.5.3 | Verify that a shopping list can be generated. | 1. Navigate to a meal plan.<br>2. Click "Generate Shopping List". | A new page is displayed showing the shopping list. | E2E |
| **TC-SL-002** | FR-1.5.2 | Verify consolidation logic for flexible units. | 1. Create a meal plan with recipes containing:<br> - 100g cheese<br> - 0.2kg cheese<br> - 1 apple<br> - 2 apples<br> - 1 can tomatoes<br> - 1 cup flour & 200g flour<br>2. Generate list. | The list should show:<br> - 300g cheese (or 0.3kg)<br> - 3 apples<br> - 1 can tomatoes<br> - 1 cup flour<br> - 200g flour (unconsolidated) | Integration |
| **TC-SL-003** | FR-1.5.4 | Verify a user can manually edit a generated shopping list. | 1. Generate a shopping list.<br>2. Click "Edit List", add/remove an item, and save. | The changes are persisted and visible on the shopping list. | E2E |

### 4.6 Future/Desired Features

| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type |
|---|---|---|---|---|---|
| **TC-FF-001** | FR-1.7.2 | Verify PDF export. (When implemented) | 1. Generate a list.<br>2. Click "Export to PDF". | A PDF file is downloaded and its content is correct. | E2E |
| **TC-FF-002** | FR-1.7.1 | Verify local recipe search. (When implemented) | 1. Search for a local recipe by name. | The list filters to show only matching recipes. | E2E |

## 5. Non-Functional Testing

| Test ID | Requirement(s) | Test Description | Test Type |
|---|---|---|---|
| **TC-NFR-001** | NFR-2.1.1, NFR-2.1.3 | Measure page load and API response times. | Performance |
| **TC-NFR-002** | NFR-2.1.2 | Measure time for recipe search and extraction. | Performance |
| **TC-NFR-003** | NFR-2.2.1, NFR-2.2.2 | Conduct exploratory testing for usability and feedback. | Manual (Usability) |
| **TC-NFR-004** | NFR-2.3.2 | Test invalid inputs and error handling. | E2E |
| **TC-NFR-005** | NFR-2.5.1 | Test the accuracy of the AI recipe extraction model. | Manual |
