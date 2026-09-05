// Persisted lists are a flat items array; group like the PDF (empty → "Other").
export const OTHER_LOCATION_GROUP = "Other";

export function resolveItemLocation(item) {
  const loc = (item && (item.location || item.location_id)) || "";
  const trimmed = String(loc).trim();
  return trimmed === "" ? OTHER_LOCATION_GROUP : trimmed;
}

export function groupItemsByLocation(items) {
  const groups = new Map();
  (items || []).forEach((item, index) => {
    const location = resolveItemLocation(item);
    if (!groups.has(location)) {
      groups.set(location, []);
    }
    groups.get(location).push({ item, index });
  });
  const keys = Array.from(groups.keys()).sort((a, b) => {
    if (a === OTHER_LOCATION_GROUP && b !== OTHER_LOCATION_GROUP) return 1;
    if (b === OTHER_LOCATION_GROUP && a !== OTHER_LOCATION_GROUP) return -1;
    return a.localeCompare(b);
  });
  return keys.map((location) => ({
    location,
    entries: groups.get(location),
  }));
}

export function formatItemLabel(item) {
  if (item.quantity && item.unit) {
    return `${item.quantity} ${item.unit} ${item.name}`;
  }
  if (item.quantity) {
    return `${item.quantity} ${item.name}`;
  }
  return item.name;
}
