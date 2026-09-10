import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const SRC = join(
  dirname(fileURLToPath(import.meta.url)),
  "components",
  "ShoppingListView.jsx",
);

describe("ShoppingListView purchased UX", () => {
  it("does not render view-mode purchased checkboxes", async () => {
    const src = await readFile(SRC, "utf8");
    assert.equal(src.includes("handleTogglePurchased"), false);
    assert.equal(src.includes('type="checkbox"'), false);
    assert.match(src, /formatSourceRecipeNames/);
    assert.match(src, /shopping-item-sources/);
  });
});
