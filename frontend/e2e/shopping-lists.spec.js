// @ts-check
import { test, expect } from "@playwright/test";

/* global process */

test.beforeEach(async ({ page }) => {
  const apiBase = process.env.API_BASE_URL || "http://localhost:5000";
  await page.request.post(`${apiBase}/api/test/seed-db`);
});

test("shopping lists are on meal plans, not a separate nav page", async ({
  page,
}) => {
  await page.goto("/ui/");
  await expect(page.getByTestId("nav-meal-plans")).toBeVisible();
  await expect(page.getByTestId("nav-shopping-lists")).toHaveCount(0);
});

test("should generate a meal-plan shopping list, fetch its PDF, and delete it", async ({
  page,
}) => {
  await page.goto("/ui/meal-plans");
  await page.getByRole("link", { name: "Weekly Meal Plan" }).click();
  await page.waitForURL("**/meal-plans/*");
  await expect(
    page.getByRole("heading", { name: "Shopping List" }),
  ).toBeVisible();

  const generateButton = page.getByTestId("shopping-generate");
  if (await generateButton.isVisible()) {
    await generateButton.click();
  }

  const pdfLink = page.getByTestId("shopping-pdf");
  await expect(pdfLink).toBeVisible();
  const href = await pdfLink.getAttribute("href");
  expect(href).toMatch(/\/shopping-lists\/.+\/pdf/);

  const apiBase = process.env.API_BASE_URL || "http://localhost:5000";
  const resp = await page.request.get(`${apiBase}${href}`);
  expect(resp.ok()).toBeTruthy();
  expect(resp.headers()["content-type"]).toMatch(/pdf/i);
  const body = await resp.body();
  expect(body.subarray(0, 4).toString()).toBe("%PDF");

  page.once("dialog", (dialog) => dialog.accept());
  await page.getByTestId("shopping-delete").click();
  await expect(page.getByTestId("shopping-generate")).toBeVisible();
});

test("edit mode orders items by location like view mode", async ({ page }) => {
  const apiBase = process.env.API_BASE_URL || "http://localhost:5000";
  const plansResp = await page.request.get(`${apiBase}/api/meal-plans`);
  expect(plansResp.ok()).toBeTruthy();
  const plans = await plansResp.json();
  const weekly = plans.find((p) => p.name === "Weekly Meal Plan");
  expect(weekly).toBeTruthy();

  const listsResp = await page.request.get(`${apiBase}/api/shopping-lists`);
  const lists = listsResp.ok() ? await listsResp.json() : [];
  for (const sl of lists) {
    if (sl.meal_plan_id === weekly.id) {
      await page.request.delete(`${apiBase}/api/shopping-lists/${sl.id}`);
    }
  }

  const created = await page.request.post(`${apiBase}/api/shopping-lists`, {
    data: { meal_plan_id: weekly.id, name: "Location Order List" },
  });
  expect(created.ok()).toBeTruthy();
  const list = await created.json();
  const updated = await page.request.put(
    `${apiBase}/api/shopping-lists/${list.id}`,
    {
      data: {
        name: list.name,
        items: [
          { name: "Salt", quantity: 1, unit: "", location: "" },
          { name: "Milk", quantity: 1, unit: "l", location: "Dairy" },
          { name: "Flour", quantity: 1, unit: "kg", location: "Pantry" },
        ],
      },
    },
  );
  expect(updated.ok()).toBeTruthy();

  await page.goto(`/ui/meal-plans/${weekly.id}`);
  await expect(
    page.getByRole("heading", { name: /Shopping List:/ }),
  ).toBeVisible();

  await expect(page.getByRole("heading", { name: "Dairy" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Pantry" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Other" })).toBeVisible();

  await page.getByRole("button", { name: "Edit" }).first().click();

  await expect(page.getByRole("heading", { name: "Dairy" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Pantry" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Other" })).toBeVisible();

  const names = await page
    .locator("input[placeholder='Item name']")
    .evaluateAll((els) => els.map((el) => el.value));
  expect(names).toEqual(["Milk", "Flour", "Salt"]);

  const locationInputs = page.locator("input[placeholder='Location']");
  await locationInputs.first().fill("Produce");
  await locationInputs.first().blur();

  const namesAfterMove = await page
    .locator("input[placeholder='Item name']")
    .evaluateAll((els) => els.map((el) => el.value));
  expect(namesAfterMove).toEqual(["Flour", "Milk", "Salt"]);
});

test("generated items show source recipe names on hover title", async ({
  page,
}) => {
  const apiBase = process.env.API_BASE_URL || "http://localhost:5000";
  const recipesResp = await page.request.get(`${apiBase}/api/recipes`);
  expect(recipesResp.ok()).toBeTruthy();
  const recipes = await recipesResp.json();
  const plansResp = await page.request.get(`${apiBase}/api/meal-plans`);
  expect(plansResp.ok()).toBeTruthy();
  const plans = await plansResp.json();
  const weekly = plans.find((p) => p.name === "Weekly Meal Plan");
  expect(weekly).toBeTruthy();

  // seed-db recreates recipes but keeps the meal plan, so recipe IDs go
  // stale after the first test. Relink and drop leftover lists (e.g. the
  // previous spec's Location Order List) so Generate uses Classic Pancakes.
  const relinked = await page.request.put(
    `${apiBase}/api/meal-plans/${weekly.id}`,
    {
      data: {
        name: weekly.name,
        description: weekly.description,
        recipe_ids: recipes.map((r) => r.id),
      },
    },
  );
  expect(relinked.ok()).toBeTruthy();

  const listsResp = await page.request.get(`${apiBase}/api/shopping-lists`);
  expect(listsResp.ok()).toBeTruthy();
  const lists = await listsResp.json();
  for (const sl of lists) {
    if (sl.meal_plan_id === weekly.id) {
      await page.request.delete(`${apiBase}/api/shopping-lists/${sl.id}`);
    }
  }

  await page.goto("/ui/meal-plans");
  await page.getByRole("link", { name: "Weekly Meal Plan" }).click();
  await page.waitForURL("**/meal-plans/*");
  await expect(
    page.getByRole("heading", { name: "Shopping List" }),
  ).toBeVisible();
  const generateButton = page.getByTestId("shopping-generate");
  await expect(generateButton).toBeVisible();
  await generateButton.click();
  const flour = page
    .getByTestId("shopping-item-sources")
    .filter({ hasText: "Flour" });
  await expect(flour).toBeVisible();
  await expect(flour).toHaveAttribute("title", "Classic Pancakes");
});
