import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const E2E = join(dirname(fileURLToPath(import.meta.url)), "..", "e2e");

describe("e2e hygiene", () => {
  it("does not use waitForTimeout", async () => {
    const files = (await readdir(E2E)).filter((f) => f.endsWith(".spec.js"));
    for (const f of files) {
      const src = await readFile(join(E2E, f), "utf8");
      assert.equal(src.includes("waitForTimeout"), false, f);
    }
  });

  it("seedDb fails the spec when seed-db is not OK", async () => {
    const src = await readFile(join(E2E, "helpers.js"), "utf8");
    assert.match(src, /seedDb/);
    assert.match(src, /\.ok\(\)/);
  });
});
