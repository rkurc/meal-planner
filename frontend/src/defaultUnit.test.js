import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { applyDefaultUnit } from "./defaultUnit.js";

describe("applyDefaultUnit", () => {
  const units = { Milk: "cups" };

  it("fills unit when name is set and unit empty", () => {
    const row = { name: "", unit: "" };
    const next = applyDefaultUnit(row, "name", "Milk", units);
    assert.equal(next.unit, "cups");
    assert.equal(next.name, "Milk");
  });

  it("does not overwrite an existing unit", () => {
    const row = { name: "", unit: "tbsp" };
    const next = applyDefaultUnit(row, "name", "Milk", units);
    assert.equal(next.unit, "tbsp");
  });

  it("ignores non-name fields", () => {
    const row = { name: "Milk", unit: "" };
    const next = applyDefaultUnit(row, "quantity", "1", units);
    assert.equal(next.unit, "");
  });
});
