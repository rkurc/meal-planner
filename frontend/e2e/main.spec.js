// @ts-check
// IMPORTANT: All E2E execution (npm, playwright) MUST go through the meal-planner-dev Docker image.
// Example:
//   docker run --rm -v $(pwd):/app -w /app/frontend --network host meal-planner-dev sh -c 'npm ci && npx playwright install --with-deps && npx playwright test'
// (Servers started via start_and_seed.sh in another container or use container network + baseURL adjustment.)
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
  // Use /ui/ (React app) to align with all other E2E tests (BASE_URL now serves /ui/ React; legacy root is no longer primary target).
  await page.goto("/ui/");
  await expect(page).toHaveTitle(/Meal Planner/);
});

test("should navigate to the recipes page and see the seeded recipes", async ({
  page,
}) => {
  // Navigate to the recipes page (React app served at /ui/ by the gunicorn backend on 5000).
  await page.goto("/ui/");
  await page.waitForSelector("nav");
  await page.getByRole("link", { name: "Recipes", exact: true }).click();
  await page.waitForURL("**/recipes");

  // Wait for the recipe list to load and verify seeded data
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

test("should create a new recipe", async ({ page }) => {
  await page.goto("/ui/recipes");

  // Click Create New Recipe button
  await page.getByRole("link", { name: "Create New Recipe" }).click();
  await page.waitForURL("**/recipes/new");

  // Fill out the form
  await page.fill("#name", "E2E Test Recipe");
  await page.fill("#description", "A recipe created by E2E test");
  await page.fill("#source_url", "https://example.com/recipe");
  await page.fill("#instructions", "Step 1: Do this\nStep 2: Do that");

  // Add an ingredient
  await page.fill("input[placeholder='Ingredient name']", "Test Ingredient");
  await page.fill("input[placeholder='Quantity']", "2");
  await page.fill("input[placeholder='Unit']", "cups");

  // Submit the form
  await page.getByRole("button", { name: "Create Recipe" }).click();

  // Verify we're redirected to the recipe detail page
  await page.waitForURL("**/recipes/*", { waitUntil: "networkidle" });

  // Verify recipe details are displayed
  await expect(
    page.getByRole("heading", { name: "E2E Test Recipe" }),
  ).toBeVisible();
  await expect(page.getByText("A recipe created by E2E test")).toBeVisible();
  await expect(page.getByText("2 cups Test Ingredient")).toBeVisible();
});

test("should view recipe details", async ({ page }) => {
  await page.goto("/ui/recipes");

  // Click on a seeded recipe (Classic Pancakes from RECIPES_TO_SEED) using role for strict match (avoids description text)
  await page.getByRole("heading", { name: "Classic Pancakes" }).click();

  // Verify we're on the detail page
  await page.waitForURL("**/recipes/*");

  // Verify recipe details are visible
  await expect(
    page.getByRole("heading", { name: "Classic Pancakes" }),
  ).toBeVisible();
  // Edit is a <Link> (role link), Delete is <button> (see RecipeDetail.jsx)
  await expect(page.getByRole("link", { name: "Edit Recipe" })).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Delete Recipe" }),
  ).toBeVisible();
});

test("should edit an existing recipe", async ({ page }) => {
  await page.goto("/ui/recipes");

  // Click on a seeded recipe (Classic Pancakes from RECIPES_TO_SEED) using role for strict match (avoids description text)
  await page.getByRole("heading", { name: "Classic Pancakes" }).click();
  await page.waitForURL("**/recipes/*");

  // Click Edit button
  await page.getByRole("link", { name: "Edit Recipe" }).click();
  await page.waitForURL("**/recipes/*/edit");

  // Update the description
  await page.fill("#description", "Updated description by E2E test");

  // Submit the form
  await page.getByRole("button", { name: "Update Recipe" }).click();

  // Verify we're back on the detail page
  await page.waitForURL("**/recipes/*", { waitUntil: "networkidle" });

  // Verify the update is reflected
  await expect(page.getByText("Updated description by E2E test")).toBeVisible();
});

test("should delete a recipe", async ({ page }) => {
  // First create a recipe to delete (navigate via list + link like create test for reliable form init)
  await page.goto("/ui/recipes");

  // Click Create New Recipe link
  await page.getByRole("link", { name: "Create New Recipe" }).click();
  await page.waitForURL("**/recipes/new");

  await page.fill("#name", "Recipe to Delete");
  await page.fill("#instructions", "This will be deleted");
  await page.getByRole("button", { name: "Create Recipe" }).click();
  await page.waitForURL("**/recipes/*", { waitUntil: "networkidle" });

  // Ensure delete button is ready (from detail page)
  await expect(
    page.getByRole("button", { name: "Delete Recipe" }),
  ).toBeVisible();

  // Set up dialog handler before clicking delete
  page.on("dialog", (dialog) => dialog.accept());

  // Click Delete button
  await page.getByRole("button", { name: "Delete Recipe" }).click();

  // Verify we're redirected to the recipe list
  await page.waitForURL("**/recipes", { waitUntil: "networkidle" });

  // Verify the recipe is no longer in the list (use exact + role for strict match)
  await expect(
    page.getByRole("heading", { name: "Recipe to Delete" }),
  ).not.toBeVisible();
});

test("should generate shopping list from meal plan", async ({ page }) => {
  await page.goto("/ui/meal-plans");
  // Use specific role link (name in MealPlanList) + exact to avoid any ambiguity/strict mode
  await page.getByRole("link", { name: "Weekly Meal Plan" }).click();
  await page.waitForURL("**/meal-plans/*");

  // Verify shopping list section is visible
  await expect(
    page.getByRole("heading", { name: /Shopping List/ }),
  ).toBeVisible();

  // Check if "Generate Shopping List" button exists (if not already generated)
  const generateButton = page.getByRole("button", {
    name: "Generate Shopping List",
  });
  const editButton = page.getByRole("button", { name: "Edit" });

  if (await generateButton.isVisible()) {
    // Generate the shopping list
    await generateButton.click();

    // Wait for the list to be generated
    await page.waitForTimeout(1000);

    // Verify the shopping list is now visible
    await expect(editButton).toBeVisible();
  }
});

test("should edit shopping list items", async ({ page }) => {
  await page.goto("/ui/meal-plans");
  // Use specific role link (name in MealPlanList) + exact to avoid any ambiguity/strict mode
  await page.getByRole("link", { name: "Weekly Meal Plan" }).click();
  await page.waitForURL("**/meal-plans/*");

  // Wait for shopping section to be ready (avoids undefined click)
  await page.waitForSelector("text=Shopping List", { timeout: 10000 });

  // Generate shopping list if not already present
  const generateButton = page.getByRole("button", {
    name: "Generate Shopping List",
  });
  if (await generateButton.isVisible()) {
    await generateButton.click();
    await page.waitForSelector("text=Edit", { timeout: 5000 }); // wait for edit to appear after generate
  }

  // Click Edit button for shopping list (use first visible "Edit" button; meal plan edit is a link not button)
  await page.getByRole("button", { name: "Edit" }).first().click();

  // Add a new item
  await page.getByRole("button", { name: "Add Item" }).click();

  // Find the last ingredient input set and fill it
  const nameInputs = await page.locator("input[placeholder='Item name']").all();
  const lastNameInput = nameInputs[nameInputs.length - 1];
  await lastNameInput.fill("E2E Test Item");

  const qtyInputs = await page.locator("input[placeholder='Qty']").all();
  const lastQtyInput = qtyInputs[qtyInputs.length - 1];
  await lastQtyInput.fill("5");

  const unitInputs = await page.locator("input[placeholder='Unit']").all();
  const lastUnitInput = unitInputs[unitInputs.length - 1];
  await lastUnitInput.fill("kg");

  // Save the changes
  await page.getByRole("button", { name: "Save" }).click();

  // Wait for save confirmation
  page.on("dialog", (dialog) => dialog.accept());
  await page.waitForTimeout(500);

  // Verify the item is in the list
  await expect(page.getByText("5 kg E2E Test Item")).toBeVisible();
});
