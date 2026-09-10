import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { formDataFromDraft } from "./recipeDraft.js";

describe("formDataFromDraft", () => {
  it("returns null for missing drafts", () => {
    assert.equal(formDataFromDraft(null), null);
    assert.equal(formDataFromDraft(undefined), null);
  });

  it("maps parse API payload onto RecipeForm state", () => {
    const form = formDataFromDraft({
      name: "Zupa",
      description: "Obiad",
      instructions: "Gotować.",
      source_url: "https://example.com/zupa",
      ingredients: [
        { name: "woda", quantity: 1, unit: "l", location: "" },
        { name: "  ", quantity: "2", unit: "g" },
      ],
      meta: { parser: "llm", model: "qwen2.5:1.5b" },
    });
    assert.deepEqual(form, {
      name: "Zupa",
      description: "Obiad",
      source_url: "https://example.com/zupa",
      instructions: "Gotować.",
      ingredients: [{ name: "woda", quantity: "1", unit: "l", location: "" }],
    });
  });

  it("keeps one empty ingredient row when none were extracted", () => {
    const form = formDataFromDraft({
      name: "Chleb",
      instructions: "Upiec.",
      ingredients: [],
    });
    assert.equal(form.name, "Chleb");
    assert.deepEqual(form.ingredients, [
      { name: "", quantity: "", unit: "", location: "" },
    ]);
  });
});
