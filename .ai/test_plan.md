# Detailed Test Plan

## 1. Introduction

This document outlines the test plan for the Meal Planner application. Its purpose is to provide a comprehensive strategy for verifying the functionality, reliability, and performance of the system. This plan is based on the features and requirements defined in `feature_summary.md` and `requirements.md`.

## 2. Scope

**Overall status note (2026-06-16, reconciled):**
- Core features (Recipe/MealPlan/Shopping CRUD + gen) are *implemented* and tested (65 backend tests + 8 E2E).
- Automatic Discovery (ARD) and standalone Ingredient mgmt (ING) are *not implemented*.
- E2E tests exist for React recipe + mealplan + shopping workflows and pass after seed fixes.
- PDF and advanced search are legacy-only or not present in React.
- All verifications use Docker dev image where applicable.

### 2.1 In Scope

*   Testing of implemented features: Recipe Management, Meal Plan Management, Shopping List Generation (full in API + React + legacy).
*   Verification of both the traditional Jinja2-based UI and the modern React-based UI (current parity for implemented domains).
*   Testing of full API endpoints (`/api/recipes`, `/api/meal-plans`, `/api/shopping-lists`).
*   Backend unit/integration for CRUD, shopping consolidation logic.
*   E2E flows for recipe CRUD, meal plan, shopping list view/edit.

### 2.2 Out of Scope (or Future when features added)

*   This document does not include the *implementation* of the tests, only the plan.
*   Testing of third-party dependencies (e.g., the Flask framework itself) is not in scope.
*   Automatic Recipe Discovery features (search/extract) and their tests (TC-ARD-*) until implemented.
*   Standalone Ingredient Management tests (TC-ING-*) until implemented.
*   Full NFR performance/AI accuracy until relevant features exist.
*   PDF export from React UI.

## 3. Test Strategy

A multi-layered testing approach will be used:

*   **Unit Tests:** To test individual functions and components in isolation. `pytest` for the backend and React Testing Library/Jest for the frontend are recommended.
*   **Integration Tests:** To test the interaction between components, such as the interaction between the Flask routes and the database logic.
*   **API Tests:** To directly test the `/api/recipes` endpoint for correctness, error handling, and performance. Tools like `Postman` or `pytest` with an HTTP client can be used.
*   **End-to-End (E2E) Tests:** To simulate real user workflows in a browser. This is critical for testing both the Jinja2 and React UIs. Tools like `Playwright` or `Cypress` are recommended.
*   **Manual Testing:** For exploratory testing and validating usability requirements that are difficult to automate.

## 4. Test Cases

### 4.1 Automatic Recipe Discovery *(NOT IMPLEMENTED - ALL TESTS FUTURE)*

**Status:** No discovery UI, no backend, no extraction. These tests cannot pass until feature work. (Grep in Docker + source confirms zero relevant code.)

#### 4.1.1 Search-Based Discovery
| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type | Status |
|---|---|---|---|---|---|---|
| **TC-ARD-S-001** | FR-1.1.1.1, FR-1.1.1.2 | Verify user can search for recipes by dish type. | 1. Navigate to "Discover Recipes".<br>2. Enter "chicken pasta" into the search field.<br>3. Submit the search. | The system displays a list of links to recipes related to "chicken pasta". | E2E | Not implemented - future |
| **TC-ARD-S-002** | FR-1.1.1.3, FR-1.1.1.4 | Verify user can select a search result for extraction. | 1. Perform a search.<br>2. Click the "Import" or "Extract" button next to a valid search result. | The system proceeds to the URL-based extraction workflow for the selected link. | E2E | Not implemented - future |

#### 4.1.2 URL-Based Extraction
| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type | Status |
|---|---|---|---|---|---|---|
| **TC-ARD-U-001** | FR-1.1.2.1, FR-1.1.2.2 | Verify user can submit a URL for extraction. | 1. Navigate to "Import from URL".<br>2. Enter a valid recipe URL.<br>3. Click "Extract". | The system shows a loading/progress indicator and begins the extraction process. | E2E | Not implemented - future |
| **TC-ARD-U-002** | FR-1.1.2.3, FR-1.1.2.4 | Verify recipe data is extracted and presented for confirmation. | 1. Submit a valid URL for extraction. | The "Add Recipe" form is displayed, pre-filled with the extracted name, instructions, and ingredients for user review. | Integration | Not implemented - future |
| **TC-ARD-U-003** | NFR-2.3.2 | Verify system handles a non-recipe URL gracefully. | 1. Submit a URL that is not a recipe (e.g., google.com). | The system displays a user-friendly error message, such as "Could not find a recipe at the provided URL." | E2E | Not implemented - future |

### 4.2 Recipe Management *(IMPLEMENTED)*

**Status:** All tests in this section pass (covered by 65 pytest + 8 E2E Playwright). Full parity in React + API + legacy. (Note: E2E paths use `/static/react_app/recipes` etc.)

| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type | Status |
|---|---|---|---|---|---|---|
| **TC-REC-001** | FR-1.2.1, FR-1.2.2 | Verify user can create a recipe with all metadata. | 1. Navigate to "Add Recipe".<br>2. Fill in all fields, including times and shelf-life.<br>3. Submit. | The new recipe is created and visible in the recipe list. | E2E | Implemented (passes) |
| **TC-REC-002** | FR-1.2.3, FR-1.2.4 | Verify recipe list and detail pages display correctly. | 1. Navigate to the recipe list.<br>2. Click on a recipe. | All recipes are listed. The detail page shows all saved metadata correctly. | E2E | Implemented (passes) |
| **TC-REC-003** | FR-1.2.5 | Verify a user can edit an existing recipe. | 1. Navigate to a recipe's detail page.<br>2. Click "Edit" and change a field.<br>3. Submit. | The recipe's details are updated with the new information. | E2E | Implemented (passes) |
| **TC-REC-004** | FR-1.2.6 | Verify a user can delete a recipe. | 1. Navigate to a recipe's detail page.<br>2. Click "Delete" and confirm. | The recipe is removed from the recipe list. | E2E | Implemented (passes) |
| **TC-REC-005** | FR-1.2.7 | Verify the `/api/recipes` endpoint returns a list of recipes. | 1. Send a GET request to `/api/recipes`. | The API returns a `200 OK` status with a JSON array of recipe objects. | API | Implemented (passes) |
| **TC-REC-006** | FR-1.6.3 | Verify that recipes are displayed on the React UI. | 1. Navigate to the `/ui/` page. | The page loads and displays a list of recipes fetched from the API. | E2E | Implemented (passes; see E2E) |
| **TC-REC-007** | FR-1.3.4 | Verify recipe can be created with flexible ingredient units. | 1. Create a recipe.<br>2. Add an ingredient with quantity "250" and unit "g".<br>3. Add another with "1" and "can".<br>4. Save. | The recipe saves and displays the ingredients with their correct flexible units. | E2E | Implemented (passes) |

### 4.3 Ingredient Management *(NOT IMPLEMENTED - ALL TESTS FUTURE)*

**Status:** No "Manage Ingredients" page, no master list, no standalone endpoints. Only embedded in recipes. These map to future work.

| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type | Status |
|---|---|---|---|---|---|---|
| **TC-ING-001** | FR-1.3.1 | Verify a user can create a new ingredient. | 1. Navigate to "Manage Ingredients".<br>2. Click "Add Ingredient", enter a name, and save. | The new ingredient appears in the master list. | E2E | Not implemented - future |
| **TC-ING-002** | FR-1.3.2 | Verify the ingredient list page displays all items. | 1. Navigate to "Manage Ingredients". | All created ingredients are displayed. | E2E | Not implemented - future |
| **TC-ING-003** | FR-1.3.3 | Verify a user can edit or delete an ingredient. | 1. From the ingredient list, edit or delete an item. | The ingredient is updated or removed from the list. | E2E | Not implemented - future |

### 4.4 Meal Plan Management *(IMPLEMENTED)*

**Status:** Implemented and covered by backend tests + E2E ("should generate shopping list from meal plan").

| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type | Status |
|---|---|---|---|---|---|---|
| **TC-MP-001** | FR-1.4.1, FR-1.4.2 | Verify a user can create a meal plan and add recipes. | 1. Navigate to "Create Meal Plan".<br>2. Name the plan, add recipes, and save. | The new meal plan is created and displayed, showing the selected recipes. | E2E | Implemented (passes) |
| **TC-MP-002** | FR-1.4.4 | Verify that a user can edit or delete a meal plan. | 1. From the meal plan list, edit or delete a plan. | The plan is updated or removed from the list. | E2E | Implemented (passes) |

### 4.5 Shopping List Generation *(IMPLEMENTED)*

**Status:** Generation, consolidation (in backend tests), persistence (via shopping list API), edit, and E2E ("should generate...", "should edit shopping list items") all covered and green. (65 tests include `test_shopping_list*`.)

| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type | Status |
|---|---|---|---|---|---|---|
| **TC-SL-001** | FR-1.5.1, FR-1.5.3 | Verify that a shopping list can be generated. | 1. Navigate to a meal plan.<br>2. Click "Generate Shopping List". | A new page is displayed showing the shopping list. | E2E | Implemented (passes) |
| **TC-SL-002** | FR-1.5.2 | Verify consolidation logic for flexible units. | 1. Create a meal plan with recipes containing:<br> - 100g cheese<br> - 0.2kg cheese<br> - 1 apple<br> - 2 apples<br> - 1 can tomatoes<br> - 1 cup flour & 200g flour<br>2. Generate list. | The list should show:<br> - 300g cheese (or 0.3kg)<br> - 3 apples<br> - 1 can tomatoes<br> - 1 cup flour<br> - 200g flour (unconsolidated) | Integration | Implemented (passes via unit tests) |
| **TC-SL-003** | FR-1.5.4 | Verify a user can manually edit a generated shopping list. | 1. Generate a shopping list.<br>2. Click "Edit List", add/remove an item, and save. | The changes are persisted and visible on the shopping list. | E2E | Implemented (passes) |

### 4.6 Future/Desired Features

| Test ID | Requirement(s) | Test Description | Test Steps | Expected Result | Test Type | Status |
|---|---|---|---|---|---|---|
| **TC-FF-001** | FR-1.7.2 | Verify PDF export. (When implemented) | 1. Generate a list.<br>2. Click "Export to PDF". | A PDF file is downloaded and its content is correct. | E2E | Partial (legacy Jinja only; React not implemented) |
| **TC-FF-002** | FR-1.7.1 | Verify local recipe search. (When implemented) | 1. Search for a local recipe by name. | The list filters to show only matching recipes. | E2E | Partial (basic legacy search; React none) |

## 5. Non-Functional Testing

**Note:** Many NFRs (esp. around discovery) are aspirational until features are added. Current E2E + pytest cover implemented paths and basic error handling.

| Test ID | Requirement(s) | Test Description | Test Type | Status |
|---|---|---|---|---|
| **TC-NFR-001** | NFR-2.1.1, NFR-2.1.3 | Measure page load and API response times. | Performance | Not measured (dev responsive) |
| **TC-NFR-002** | NFR-2.1.2 | Measure time for recipe search and extraction. | Performance | Future (no discovery) |
| **TC-NFR-003** | NFR-2.2.1, NFR-2.2.2 | Conduct exploratory testing for usability and feedback. | Manual (Usability) | Applicable to current UIs |
| **TC-NFR-004** | NFR-2.3.2 | Test invalid inputs and error handling. | E2E | Covered in CRUD tests |
| **TC-NFR-005** | NFR-2.5.1 | Test the accuracy of the AI recipe extraction model. | Manual | Future (no AI/extraction) |
