# Migration Plan: From Jinja2 to a Headless API

## 1. Introduction

This document outlines a strategic plan for migrating the Meal Planner application from its current hybrid architecture (part server-rendered Jinja2, part React) to a modern, fully decoupled architecture consisting of a headless Flask API and a comprehensive React single-page application (SPA).

**Goal:** To improve scalability, developer experience, and user experience by completing the transition to a modern web architecture.

## 2. Current State vs. Target State

**Reconciliation note (2026-06-16):** Phase 1 largely complete; Phase 2 complete for recipes + meal plans + shopping; Phase 3 not started. (See below.)

*   **Current State:** A Flask application that serves both a JSON API (`/api/*`) and server-rendered HTML pages via Jinja2 templates. A separate React application exists at `/static/react_app/` (and `/ui/`) providing *full parity* for recipes, meal plans, and shopping lists on top of the complete API. Legacy Jinja2 still fully functional.
*   **Target State:** A "headless" Flask application that functions exclusively as a JSON API server. A single, comprehensive React application that handles all user interface rendering and interacts with the Flask backend via the API. (Auth still missing for secure production use.)

## 3. Phased Migration Strategy

A phased approach is recommended to minimize risk and ensure a smooth transition.

### Phase 1: Solidify the API Foundation *(LARGELY COMPLETE for recipes/mealplans/shopping)*

The API is the backbone of the target architecture. Before migrating more UI features, the API must be robust and complete.

*   **Action 1.1: Full API Coverage.** ... *(Completed: full CRUD + associations + shopping gen for recipes, meal-plans, shopping-lists. Verified in code + 65 tests.)*
*   **Action 1.2: API Authentication.** Implement a secure authentication/authorization mechanism for the API (e.g., using tokens like JWT). This is critical once the UI is fully decoupled. *(NOT STARTED)*
*   **Action 1.3: API Documentation.** Document all API endpoints clearly using a standard like OpenAPI (Swagger). This will be essential for frontend development. *(Not done.)*

### Phase 2: Achieve Feature Parity in React *(COMPLETE for core features)*

The goal of this phase is to rebuild all features currently handled by Jinja2 within the React application.

*   **Action 2.1: Prioritize and Migrate.** ... *(Recipes full CRUD migrated to React; Meal Plan full incl. form fixes (PR); Shopping list view/edit via ShoppingListView integrated. E2E 8 tests pass.)*
*   **Action 2.2: Consistent UI/UX.** ... *(React components implemented; parity achieved.)*
*   **Action 2.3: Comprehensive Testing.** ... *(Backend 65 tests green; E2E green covering React recipe + mealplan + shopping flows post-seed.)*

**Current parity achieved for:** recipes, meal plans, shopping lists. (Discovery and ingredients not applicable yet.)

### Phase 3: Decommission Legacy Components *(NOT STARTED)*

Once all features have been successfully migrated to and verified in the React application, the old components can be removed.

*   **Action 3.1: Remove Jinja2 Routes.** Delete the Flask routes that were responsible for rendering the now-obsolete HTML pages. For example, the route for `/recipes/add` would be removed, as this is now handled by the React frontend.
*   **Action 3.2: Remove Template Files.** Delete the associated Jinja2 template files (`.html`) from the `templates` directory.
*   **Action 3.3: Final Cleanup.** Remove any parts of the Flask application that were solely in support of the Jinja2 rendering (e.g., specific form handling libraries if they are no longer needed).

**Note:** Legacy is still the complete fallback; no removal yet. Coexistence is current state.

## 4. Key Considerations

*   **API Design:** A well-designed and consistent API is the most critical success factor.
*   **Testing:** Rigorous E2E testing is essential to prevent regressions during the migration.
*   **Deployment:** The frontend and backend can be deployed independently in the target state, but the process needs to be planned. The React app can be served as static files from a CDN or from the Flask server itself.

## 5. Recommended First Steps *(Historical / Superseded)*

The original recommended steps (meal plans API + React) have been completed.

**Current next migration steps would be:**
1. Auth for API (Phase 1 remaining).
2. PDF export + advanced search in React.
3. Discovery + Ingredients features.
4. (Eventually) Phase 3 decommission.

See `.ai/next_step.md` for project priority.
