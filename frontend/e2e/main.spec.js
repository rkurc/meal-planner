// @ts-check
import { test, expect } from "@playwright/test";

test("homepage has expected title", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Meal Planner/);
});

test("should navigate to the recipes page", async ({
  page,
}) => {
  page.on('console', msg => console.log(`CONSOLE: ${msg.text()}`));
  page.on('pageerror', exception => console.log(`PAGE ERROR: "${exception}"`));

  await page.goto("/static/react_app/");
  await page.waitForSelector('nav');
  await page.getByText('Recipes', { exact: true }).click();
  await page.waitForURL('**/recipes');
  // Verify we're on the recipes page by checking the URL
  expect(page.url()).toContain('/recipes');
});
