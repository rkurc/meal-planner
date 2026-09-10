// @ts-check
import { test, expect } from "@playwright/test";
import { seedDb } from "./helpers.js";

test.beforeEach(async ({ page }) => {
  await seedDb(page);
});

test("should list seeded ingredients and block deleting one in use", async ({
  page,
}) => {
  await page.goto("/ui/ingredients");
  await expect(
    page.getByRole("heading", { name: "Ingredients" }),
  ).toBeVisible();
  await expect(page.getByRole("link", { name: "Flour" })).toBeVisible();

  await page.getByRole("link", { name: "Flour" }).click();
  await page.waitForURL("**/ingredients/*");
  await expect(page.getByRole("heading", { name: "Flour" })).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Classic Pancakes" }),
  ).toBeVisible();

  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Delete Ingredient" }).click();
  await expect(page.getByText(/Cannot delete: still used by/)).toBeVisible();
});

test("should create, edit, and delete a master ingredient", async ({
  page,
}) => {
  await page.goto("/ui/ingredients");
  await page.getByRole("link", { name: "Add ingredient" }).click();
  await page.waitForURL("**/ingredients/new");

  await page.fill("#name", "E2E Unique Spice");
  await page.fill("#default_unit", "tsp");
  await page.fill("#location", "Spices");
  await page.getByRole("button", { name: "Create Ingredient" }).click();
  await page.waitForURL("**/ingredients/*");

  await expect(
    page.getByRole("heading", { name: "E2E Unique Spice" }),
  ).toBeVisible();
  await expect(page.getByText("tsp")).toBeVisible();
  await expect(page.getByText("Spices")).toBeVisible();

  await page.getByRole("link", { name: "Edit Ingredient" }).click();
  await page.waitForURL("**/ingredients/*/edit");
  await page.fill("#location", "Pantry");
  await page.getByRole("button", { name: "Update Ingredient" }).click();
  await page.waitForURL("**/ingredients/*");
  await expect(page.getByText("Pantry")).toBeVisible();

  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Delete Ingredient" }).click();
  await page.waitForURL("**/ingredients");
  await expect(
    page.getByRole("link", { name: "E2E Unique Spice" }),
  ).not.toBeVisible();
});
