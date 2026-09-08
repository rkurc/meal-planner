// @ts-check
import { test, expect } from "@playwright/test";

/* global process */

test.beforeEach(async ({ page }) => {
  const apiBase = process.env.API_BASE_URL || "http://localhost:5000";
  await page.request.post(`${apiBase}/api/test/seed-db`);
});

test("should create a standalone shopping list, fetch its PDF, and delete it", async ({
  page,
}) => {
  await page.goto("/ui/shopping-lists");
  await expect(
    page.getByRole("heading", { name: "Shopping Lists" }),
  ).toBeVisible();

  page.once("dialog", (dialog) => dialog.accept("E2E Standalone List"));
  await page.getByRole("button", { name: "Create New Shopping List" }).click();
  await expect(
    page.getByRole("heading", { name: /E2E Standalone List/ }),
  ).toBeVisible();

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
  await page.getByRole("button", { name: "Delete" }).click();
  await expect(page.getByText("E2E Standalone List")).not.toBeVisible();
});

test("edit mode orders items by location like view mode", async ({ page }) => {
  const apiBase = process.env.API_BASE_URL || "http://localhost:5000";
  const listName = `Location Order List ${Date.now()}-${Math.random()
    .toString(36)
    .slice(2, 8)}`;
  const created = await page.request.post(`${apiBase}/api/shopping-lists`, {
    data: { name: listName },
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

  await page.goto("/ui/shopping-lists");
  const row = page.locator("li").filter({ hasText: listName });
  await expect(row).toHaveCount(1);
  await row.getByRole("button", { name: "View/Edit" }).click();
  await expect(
    page.getByRole("heading", { name: `Shopping List: ${listName}` }),
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
