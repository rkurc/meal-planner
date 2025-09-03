# Migration Plan: From Jinja2 to a Headless API

## 1. Introduction

This document outlines a strategic plan for migrating the Meal Planner application from its current hybrid architecture (part server-rendered Jinja2, part React) to a modern, fully decoupled architecture consisting of a headless Flask API and a comprehensive React single-page application (SPA).

**Goal:** To improve scalability, developer experience, and user experience by completing the transition to a modern web architecture.

## 2. Current State vs. Target State

*   **Current State:** A Flask application that serves both a JSON API (`/api/*`) and server-rendered HTML pages via Jinja2 templates. A separate React application exists at `/ui/` for some features.
*   **Target State:** A "headless" Flask application that functions exclusively as a JSON API server. A single, comprehensive React application that handles all user interface rendering and interacts with the Flask backend via the API.

## 3. Phased Migration Strategy

A phased approach is recommended to minimize risk and ensure a smooth transition.

### Phase 1: Solidify the API Foundation

The API is the backbone of the target architecture. Before migrating more UI features, the API must be robust and complete.

*   **Action 1.1: Full API Coverage.** Audit the existing Jinja2 pages. Identify all data and functionality they provide and ensure there is a corresponding API endpoint for each. For example, if meal plans are only managed via Jinja2, create full CRUD API endpoints for them (`/api/meal-plans`).
*   **Action 1.2: API Authentication.** Implement a secure authentication/authorization mechanism for the API (e.g., using tokens like JWT). This is critical once the UI is fully decoupled.
*   **Action 1.3: API Documentation.** Document all API endpoints clearly using a standard like OpenAPI (Swagger). This will be essential for frontend development.

### Phase 2: Achieve Feature Parity in React

The goal of this phase is to rebuild all features currently handled by Jinja2 within the React application.

*   **Action 2.1: Prioritize and Migrate.** Create a list of all pages/features currently rendered by Jinja2 (e.g., Recipe CRUD, Meal Plan CRUD, Shopping List Generation). Migrate them one by one into the React application. A good pilot candidate would be the "Meal Plan Management" feature.
*   **Action 2.2: Consistent UI/UX.** Ensure the new React components match or improve upon the user experience of the old pages.
*   **Action 2.3: Comprehensive Testing.** For each migrated feature, write end-to-end tests to verify that the new React-based workflow is functionally identical to the old Jinja2-based one.

### Phase 3: Decommission Legacy Components

Once all features have been successfully migrated to and verified in the React application, the old components can be removed.

*   **Action 3.1: Remove Jinja2 Routes.** Delete the Flask routes that were responsible for rendering the now-obsolete HTML pages. For example, the route for `/recipes/add` would be removed, as this is now handled by the React frontend.
*   **Action 3.2: Remove Template Files.** Delete the associated Jinja2 template files (`.html`) from the `templates` directory.
*   **Action 3.3: Final Cleanup.** Remove any parts of the Flask application that were solely in support of the Jinja2 rendering (e.g., specific form handling libraries if they are no longer needed).

## 4. Key Considerations

*   **API Design:** A well-designed and consistent API is the most critical success factor.
*   **Testing:** Rigorous E2E testing is essential to prevent regressions during the migration.
*   **Deployment:** The frontend and backend can be deployed independently in the target state, but the process needs to be planned. The React app can be served as static files from a CDN or from the Flask server itself.

## 5. Recommended First Steps

1.  Create API endpoints for full CRUD functionality on **Meal Plans**.
2.  Implement the Meal Plan management interface in React, using the new API endpoints.
3.  Once verified, remove the old Jinja2-based Meal Plan pages.
