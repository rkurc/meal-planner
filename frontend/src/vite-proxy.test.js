import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const CONFIG = join(
  dirname(fileURLToPath(import.meta.url)),
  "..",
  "vite.config.js",
);

describe("Vite dev proxy", () => {
  it("proxies API and PDF Flask paths", async () => {
    const src = await readFile(CONFIG, "utf8");
    assert.match(src, /["']\/api["']/);
    assert.match(src, /["']\/shopping-lists["']/);
    assert.match(src, /["']\/meal-plans["']/);
  });
});
