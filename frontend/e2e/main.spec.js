// @ts-check
import { test, expect } from "@playwright/test";

test("homepage has expected title", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Meal Planner/);
});

test("should navigate to the recipes page and see seeded recipes", async ({
  page,
}) => {
  await page.goto("/");
  await page.click("text=Recipes");
  await expect(page.getByText("Spaghetti Bolognese")).toBeVisible();
  await expect(page.getByText("Classic Chicken Salad")).toBeVisible();
});
