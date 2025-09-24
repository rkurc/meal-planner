// @ts-check
import { test, expect } from "@playwright/test";

// Seed the database before each test in this file
test.beforeEach(async ({ page }) => {
  // We need to call the API backend directly, not the vite dev server
  await page.request.post("http://127.0.0.1:5000/api/test/seed-db");
});

test("homepage has expected title", async ({ page }) => {
  await page.goto("/static/react_app/");
  await expect(page).toHaveTitle(/Meal Planner/);
});

test("should navigate to the recipes page and see the seeded recipes", async ({
  page,
}) => {
  // Go directly to the recipes page, including the basename
  await page.goto("/static/react_app/recipes");

  // Check that the "No recipes found." message is gone.
  await expect(page.getByText("No recipes found.")).not.toBeVisible();

  // Check that our seeded recipes are now visible using a more specific selector.
  await expect(
    page.getByRole("heading", { name: "Classic Pancakes" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Simple Omelette" }),
  ).toBeVisible();
});
