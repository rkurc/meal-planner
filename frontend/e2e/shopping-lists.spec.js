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
