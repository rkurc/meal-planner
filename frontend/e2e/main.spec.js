// @ts-check
import { test, expect } from "@playwright/test";

/* global process */

// Seed the database before each test in this file (enables reliable E2E
// against gunicorn in the integration test container, which does not use
// start_and_seed.sh). The URL is configurable for different environments
// (container networking, local ports, etc.).
test.beforeEach(async ({ page }) => {
  // Call the API backend directly (not via the Vite dev server / baseURL).
  const apiBase = process.env.API_BASE_URL || "http://localhost:5000";
  await page.request.post(`${apiBase}/api/test/seed-db`);
});

test("homepage has expected title", async ({ page }) => {
  await page.goto("/static/react_app/");
  await expect(page).toHaveTitle(/Meal Planner/);
});

test("should navigate to the recipes page and see the seeded recipes", async ({
  page,
}) => {
  // Go directly to the recipes page, including the basename used by the
  // React router (see src/App.jsx). The assets are served either via Flask
  // (/static/react_app) or the http.server in the integration job (port 5173).
  await page.goto("/static/react_app/recipes");

  // Check that the "No recipes found." message is gone.
  await expect(page.getByText("No recipes found.")).not.toBeVisible();

  // Check that our seeded recipes are now visible using a more specific selector.
  // Recipe names must be kept in sync with RECIPES_TO_SEED in
  // ../../meal_planner_app/seed_db.py (the single source of truth for the
  // test data + the /api/test/seed-db implementation).
  await expect(
    page.getByRole("heading", { name: "Classic Pancakes" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Simple Omelette" }),
  ).toBeVisible();
});
