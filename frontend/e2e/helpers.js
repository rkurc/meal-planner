// @ts-check
/* global process */
import { expect } from "@playwright/test";

/** POST /api/test/seed-db against the API backend (not the Vite baseURL). */
export async function seedDb(page) {
  const apiBase = process.env.API_BASE_URL || "http://localhost:5000";
  await page.request.post(`${apiBase}/api/test/seed-db`);
}

/**
 * After A1, seed wipes shopping lists. Click Generate if present;
 * otherwise a list must already exist. Fail if neither.
 */
export async function ensureShoppingList(page) {
  const generateButton = page.getByTestId("shopping-generate");
  const editButton = page.getByRole("button", { name: "Edit" });
  await expect(generateButton.or(editButton)).toBeVisible();
  if (await generateButton.isVisible()) {
    await generateButton.click();
  }
  await expect(editButton).toBeVisible();
}
