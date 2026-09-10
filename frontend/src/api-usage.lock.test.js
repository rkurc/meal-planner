import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const COMPONENTS = join(dirname(fileURLToPath(import.meta.url)), "components");

describe("api client usage", () => {
  it("does not call fetch() from React components", async () => {
    const files = (await readdir(COMPONENTS)).filter((f) => f.endsWith(".jsx"));
    for (const f of files) {
      const src = await readFile(join(COMPONENTS, f), "utf8");
      assert.equal(src.includes("fetch("), false, `${f} still calls fetch(`);
    }
  });
});
