// @ts-check
/* global process */
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  // E2E specs share one backend DB and POST /api/test/seed-db resets it
  // before every test. Parallel workers race that reset (stale IDs →
  // "Recipe not found" / waitForURL timeouts). Keep this at 1.
  workers: 1,
  use: {
    baseURL: process.env.BASE_URL || "http://localhost:5173",
    locale: "en-US",
    screenshot: "only-on-failure",
  },
});
