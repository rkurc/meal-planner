import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  OTHER_LOCATION_GROUP,
  formatItemLabel,
  groupItemsByLocation,
} from "./shoppingListGroups.js";

describe("formatItemLabel", () => {
  it("joins quantity, unit, and name when all are present", () => {
    assert.equal(
      formatItemLabel({ name: "Milk", quantity: 2, unit: "cups" }),
      "2 cups Milk",
    );
  });

  it("omits unit when it is empty", () => {
    assert.equal(
      formatItemLabel({ name: "Eggs", quantity: 3, unit: "" }),
      "3 Eggs",
    );
  });

  it("falls back to the name alone", () => {
    assert.equal(formatItemLabel({ name: "Salt" }), "Salt");
  });
});

describe("groupItemsByLocation", () => {
  it("puts blank and missing locations in the Other group", () => {
    const groups = groupItemsByLocation([
      { name: "Salt", location: "" },
      { name: "Pepper" },
      { name: "Milk", location: "Dairy" },
    ]);
    const other = groups.find((g) => g.location === OTHER_LOCATION_GROUP);
    const dairy = groups.find((g) => g.location === "Dairy");
    assert.equal(other.entries.length, 2);
    assert.equal(dairy.entries.length, 1);
    assert.equal(dairy.entries[0].item.name, "Milk");
  });

  it("sorts named locations alphabetically and keeps Other last", () => {
    const groups = groupItemsByLocation([
      { name: "Milk", location: "Dairy" },
      { name: "Flour", location: "Pantry" },
      { name: "Salt", location: "" },
    ]);
    assert.deepEqual(
      groups.map((g) => g.location),
      ["Dairy", "Pantry", OTHER_LOCATION_GROUP],
    );
  });

  it("preserves original item indexes for edit-mode toggles", () => {
    const groups = groupItemsByLocation([
      { name: "A", location: "Pantry" },
      { name: "B", location: "Dairy" },
    ]);
    const dairy = groups.find((g) => g.location === "Dairy");
    assert.equal(dairy.entries[0].index, 1);
  });
});
