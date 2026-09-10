/** Map POST /api/recipes/parse JSON onto RecipeForm state. */

const EMPTY_INGREDIENT = { name: "", quantity: "", unit: "", location: "" };

export function formDataFromDraft(draft) {
  if (!draft || typeof draft !== "object") {
    return null;
  }
  const mapped = Array.isArray(draft.ingredients)
    ? draft.ingredients
        .filter((item) => item && String(item.name || "").trim())
        .map((item) => ({
          name: String(item.name || "").trim(),
          quantity: item.quantity == null ? "" : String(item.quantity),
          unit: item.unit == null ? "" : String(item.unit),
          location: item.location || "",
        }))
    : [];
  return {
    name: draft.name || "",
    description: draft.description || "",
    source_url: draft.source_url || "",
    instructions: draft.instructions || "",
    ingredients: mapped.length > 0 ? mapped : [{ ...EMPTY_INGREDIENT }],
  };
}
