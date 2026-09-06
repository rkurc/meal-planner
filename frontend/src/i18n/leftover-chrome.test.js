import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const COMPONENTS = join(
  dirname(fileURLToPath(import.meta.url)),
  "..",
  "components",
);

const FORBIDDEN = {
  "IngredientForm.jsx": [
    "Edit Ingredient",
    "Add Ingredient",
    "Create Ingredient",
    "Update Ingredient",
    "Back to Ingredients",
    "Ingredient name is required.",
    "Default unit",
  ],
  "IngredientDetail.jsx": [
    "Back to Ingredients",
    "Edit Ingredient",
    "Delete Ingredient",
    "Loading ingredient...",
    "Recipes using this ingredient",
    "No recipes found using this ingredient.",
    "Default unit:",
  ],
  "RecipeForm.jsx": [
    "These are placeholder instructions from a legacy import",
    "the source recipe",
  ],
};

describe("leftover i18n chrome", () => {
  for (const [file, needles] of Object.entries(FORBIDDEN)) {
    it(`${file} uses t() instead of leftover English chrome`, async () => {
      const src = await readFile(join(COMPONENTS, file), "utf8");
      assert.match(src, /useTranslation/);
      for (const needle of needles) {
        assert.equal(
          src.includes(needle),
          false,
          `${file} still contains ${JSON.stringify(needle)}`,
        );
      }
    });
  }
});
