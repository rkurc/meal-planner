The backend APIs for meal plans are now complete. The next step is to build the user interface in the React single-page application (SPA) to manage them.

Your task is to implement the **Meal Plan Management** feature in the React frontend.

**Requirements:**
1.  **Create React Components:** Build the necessary components for:
    *   Listing all existing meal plans (e.g., a `MealPlanList` component).
    *   Displaying a single meal plan with its details and associated recipes (e.g., a `MealPlanDetail` component).
    *   A form for creating and editing meal plans (e.g., a `MealPlanForm` component).
2.  **API Integration:**
    *   Fetch data from the `/api/meal-plans` endpoints that are already implemented.
    *   Implement functionality to create, update, and delete meal plans by making requests to the API.
3.  **Routing:** Set up client-side routes (e.g., using `react-router-dom`) for `/meal-plans`, `/meal-plans/new`, `/meal-plans/:id`, etc.
4.  **State Management:** Use appropriate state management to handle the application's data flow.
5.  **Testing:** While not explicitly defined in the test plan, consider what unit or integration tests could be added for the new components.
