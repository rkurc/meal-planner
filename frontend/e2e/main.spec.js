// @ts-check
import { test, expect } from "@playwright/test";

test("homepage has expected title", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Meal Planner/);
});

test("should display seeded recipes", async ({
  page,
}) => {
  page.on('console', msg => console.log(`CONSOLE: ${msg.text()}`));
  page.on('pageerror', exception => console.log(`PAGE ERROR: "${exception}"`));

  await page.goto("/static/react_app/");
  await page.waitForSelector('nav');
  await page.getByText('Recipes', { exact: true }).click();
  await page.waitForURL('**/recipes');

  // Wait for the recipe list to load and verify seeded data
  await expect(page.getByText("Tomato Pasta")).toBeVisible();
  await expect(page.getByText("Grilled Cheese Sandwich")).toBeVisible();
  await expect(page.getByText("No recipes found.")).not.toBeVisible();
});
