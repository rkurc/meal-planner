// @ts-check
/* global process */
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  use: {
    baseURL: process.env.BASE_URL || "http://localhost:5173",
    locale: "en-US",
    screenshot: "only-on-failure",
  },
});
