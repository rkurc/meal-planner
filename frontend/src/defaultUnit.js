export function applyDefaultUnit(row, field, value, defaultUnits) {
  const next = { ...row, [field]: value };
  if (field !== "name" || !value || (row.unit && String(row.unit).trim())) {
    return next;
  }
  const defUnit = defaultUnits[value.trim()];
  if (defUnit) next.unit = defUnit;
  return next;
}
