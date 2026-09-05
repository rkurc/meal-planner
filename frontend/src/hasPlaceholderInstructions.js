/**
 * Detect empty or legacy-import placeholder recipe instructions.
 *
 * After migrate_legacy, rows with a blank przepis or a URL-only przepis
 * get a fixed placeholder so POST /api/recipes succeeds. Those strings
 * are not real cooking steps and should be treated as missing.
 */

export const URL_ONLY_PRZEPIS_CSV =
  "See source_url for full original instructions. (auto-migrated from przepisy CSV)";

export const BLANK_PRZEPIS_CSV =
  "No instructions in the legacy export. (auto-migrated from przepisy CSV)";

/** Other known placeholders from migrate_legacy.py (odb / generic CSV). */
const OTHER_KNOWN_PLACEHOLDERS = [
  "See source_url for full original instructions. (auto-migrated from .odb)",
  "See source_url for full original instructions. (migrated from CSV)",
  "See full recipe at source_url. (Migrated from przepisy_tmp.odb)",
];

const KNOWN_PLACEHOLDERS = new Set([
  URL_ONLY_PRZEPIS_CSV,
  BLANK_PRZEPIS_CSV,
  ...OTHER_KNOWN_PLACEHOLDERS,
]);

/**
 * @param {unknown} instructions
 * @returns {boolean} true when instructions are missing or a known placeholder
 */
export function hasPlaceholderInstructions(instructions) {
  if (instructions == null) {
    return true;
  }
  const trimmed = String(instructions).trim();
  if (trimmed === "") {
    return true;
  }
  return KNOWN_PLACEHOLDERS.has(trimmed);
}
