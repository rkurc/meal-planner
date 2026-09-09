import { test } from "node:test";
import assert from "node:assert/strict";
import config from "../playwright.config.js";

test("E2E uses one worker because tests share one DB that seed-db resets", () => {
  assert.equal(config.workers, 1);
});
