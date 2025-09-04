Now that the core APIs for recipes, meal plans, and shopping lists are in place, the next critical step is to secure them. Please implement a robust authentication system for the backend API. Based on the project's modern stack, a token-based approach like JWT (JSON Web Tokens) would be appropriate.

Your task is to:
1.  Choose and integrate a suitable Flask library for JWT management (e.g., `Flask-JWT-Extended`).
2.  Create new API endpoints for user registration (`/api/auth/register`) and login (`/api/auth/login`), which will issue tokens.
3.  Protect the existing API endpoints (`/api/recipes`, `/api/meal-plans`, `/api/shopping-lists`) so that they require a valid JWT to be accessed.
4.  Update the tests for the protected endpoints to include authentication headers.
5.  Provide a plan for these changes before implementation.
