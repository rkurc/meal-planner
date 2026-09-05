import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  hasPlaceholderInstructions,
  URL_ONLY_PRZEPIS_CSV,
  BLANK_PRZEPIS_CSV,
} from "./hasPlaceholderInstructions.js";

describe("hasPlaceholderInstructions", () => {
  it("treats empty, whitespace-only, null, and undefined as placeholders", () => {
    assert.equal(hasPlaceholderInstructions(""), true);
    assert.equal(hasPlaceholderInstructions("   "), true);
    assert.equal(hasPlaceholderInstructions("\n\t"), true);
    assert.equal(hasPlaceholderInstructions(null), true);
    assert.equal(hasPlaceholderInstructions(undefined), true);
  });

  it("detects the URL-only przepisy CSV placeholder", () => {
    assert.equal(hasPlaceholderInstructions(URL_ONLY_PRZEPIS_CSV), true);
    assert.equal(
      hasPlaceholderInstructions(`  ${URL_ONLY_PRZEPIS_CSV}  `),
      true,
    );
  });

  it("detects the blank przepisy CSV placeholder", () => {
    assert.equal(hasPlaceholderInstructions(BLANK_PRZEPIS_CSV), true);
  });

  it("detects other known migrate_legacy placeholders", () => {
    assert.equal(
      hasPlaceholderInstructions(
        "See source_url for full original instructions. (auto-migrated from .odb)",
      ),
      true,
    );
    assert.equal(
      hasPlaceholderInstructions(
        "See source_url for full original instructions. (migrated from CSV)",
      ),
      true,
    );
    assert.equal(
      hasPlaceholderInstructions(
        "See full recipe at source_url. (Migrated from przepisy_tmp.odb)",
      ),
      true,
    );
  });

  it("does not flag real cooking instructions", () => {
    assert.equal(
      hasPlaceholderInstructions("Mix the flour and milk. Cook until golden."),
      false,
    );
    assert.equal(
      hasPlaceholderInstructions(
        "See source_url for full original instructions. Then also brown the onions.",
      ),
      false,
    );
  });
});
