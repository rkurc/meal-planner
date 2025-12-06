// @ts-check
import { test, expect } from "@playwright/test";

test("homepage has expected title", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Meal Planner/);
});

test("should display seeded recipes", async ({ page }) => {
  page.on("console", (msg) => console.log(`CONSOLE: ${msg.text()}`));
  page.on("pageerror", (exception) =>
    console.log(`PAGE ERROR: "${exception}"`),
  );

  await page.goto("/static/react_app/");
  await page.waitForSelector("nav");
  await page.getByText("Recipes", { exact: true }).click();
  await page.waitForURL("**/recipes");

  // Wait for the recipe list to load and verify seeded data
  await expect(page.getByText("Tomato Pasta")).toBeVisible();
  await expect(page.getByText("Grilled Cheese Sandwich")).toBeVisible();
  await expect(page.getByText("No recipes found.")).not.toBeVisible();
});

test("should create a new recipe", async ({ page }) => {
  await page.goto("/static/react_app/recipes");

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
  await expect(page.getByRole("heading", { name: "E2E Test Recipe" })).toBeVisible();
  await expect(page.getByText("A recipe created by E2E test")).toBeVisible();
  await expect(page.getByText("2 cups Test Ingredient")).toBeVisible();
});

test("should view recipe details", async ({ page }) => {
  await page.goto("/static/react_app/recipes");

  // Click on a recipe
  await page.getByText("Tomato Pasta").click();

  // Verify we're on the detail page
  await page.waitForURL("**/recipes/*");

  // Verify recipe details are visible
  await expect(page.getByRole("heading", { name: "Tomato Pasta" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Edit Recipe" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Delete Recipe" })).toBeVisible();
});

test("should edit an existing recipe", async ({ page }) => {
  await page.goto("/static/react_app/recipes");

  // Click on a recipe
  await page.getByText("Tomato Pasta").click();
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
  // First create a recipe to delete
  await page.goto("/static/react_app/recipes/new");
  await page.fill("#name", "Recipe to Delete");
  await page.fill("#instructions", "This will be deleted");
  await page.getByRole("button", { name: "Create Recipe" }).click();
  await page.waitForURL("**/recipes/*", { waitUntil: "networkidle" });

  // Set up dialog handler before clicking delete
  page.on("dialog", (dialog) => dialog.accept());

  // Click Delete button
  await page.getByRole("button", { name: "Delete Recipe" }).click();

  // Verify we're redirected to the recipe list
  await page.waitForURL("**/recipes", { waitUntil: "networkidle" });

  // Verify the recipe is no longer in the list
  await expect(page.getByText("Recipe to Delete")).not.toBeVisible();
});

test("should generate shopping list from meal plan", async ({ page }) => {
  await page.goto("/static/react_app/meal-plans");

  // Click on the first meal plan
  await page.getByText("Weekly Meal Plan").click();
  await page.waitForURL("**/meal-plans/*");

  // Verify shopping list section is visible
  await expect(page.getByRole("heading", { name: /Shopping List/ })).toBeVisible();

  // Check if "Generate Shopping List" button exists (if not already generated)
  const generateButton = page.getByRole("button", { name: "Generate Shopping List" });
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
  await page.goto("/static/react_app/meal-plans");

  // Click on the first meal plan
  await page.getByText("Weekly Meal Plan").click();
  await page.waitForURL("**/meal-plans/*");

  // Generate shopping list if not already present
  const generateButton = page.getByRole("button", { name: "Generate Shopping List" });
  if (await generateButton.isVisible()) {
    await generateButton.click();
    await page.waitForTimeout(1000);
  }

  // Click Edit button for shopping list
  const editButtons = await page.getByRole("button", { name: "Edit" }).all();
  // Click the second Edit button (first is for meal plan, second for shopping list)
  if (editButtons.length > 1) {
    await editButtons[1].click();
  } else {
    await editButtons[0].click();
  }

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

