#!/usr/bin/env node
/**
 * Plural-aware i18n key parity + ingredients.usedCount snapshot.
 */
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import i18next from "i18next";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const PLURAL_SUFFIX = /_(zero|one|two|few|many|other)$/;
const REQUIRED = {
  en: ["one", "other"],
  pl: ["one", "few", "many", "other"],
};

function flatten(obj, prefix = "") {
  const out = {};
  for (const [key, value] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (value && typeof value === "object" && !Array.isArray(value)) {
      Object.assign(out, flatten(value, path));
    } else {
      out[path] = value;
    }
  }
  return out;
}

function baseKey(key) {
  return key.replace(PLURAL_SUFFIX, "");
}

function fail(msg) {
  console.error(`i18n:check failed: ${msg}`);
  process.exitCode = 1;
}

const en = JSON.parse(
  await readFile(join(ROOT, "src/i18n/locales/en/common.json"), "utf8"),
);
const pl = JSON.parse(
  await readFile(join(ROOT, "src/i18n/locales/pl/common.json"), "utf8"),
);
const enFlat = flatten(en);
const plFlat = flatten(pl);
const enBases = new Set(Object.keys(enFlat).map(baseKey));
const plBases = new Set(Object.keys(plFlat).map(baseKey));

for (const key of enBases) {
  if (!plBases.has(key)) fail(`en key missing in pl: ${key}`);
}
for (const key of plBases) {
  if (!enBases.has(key)) fail(`pl key missing in en: ${key}`);
}

function pluralCats(flat) {
  const cats = {};
  for (const key of Object.keys(flat)) {
    const match = key.match(PLURAL_SUFFIX);
    if (!match) continue;
    const base = baseKey(key);
    cats[base] = cats[base] || new Set();
    cats[base].add(match[1]);
  }
  return cats;
}

const enCats = pluralCats(enFlat);
const plCats = pluralCats(plFlat);
for (const [base, need] of Object.entries({
  en: { map: enCats, req: REQUIRED.en },
  pl: { map: plCats, req: REQUIRED.pl },
})) {
  for (const [key, have] of Object.entries(need.map)) {
    for (const cat of need.req) {
      if (!have.has(cat)) {
        fail(`${base} plural ${key} missing _${cat}`);
      }
    }
  }
}

if (enBases.has("ingredients.usedCount")) {
  await i18next.init({
    lng: "en",
    fallbackLng: "en",
    resources: {
      en: { common: en },
      pl: { common: pl },
    },
    ns: ["common"],
    defaultNS: "common",
    interpolation: { escapeValue: false },
  });
  const counts = [0, 1, 2, 5, 22];
  const expected = {
    en: {
      0: "Used in 0 recipes",
      1: "Used in 1 recipe",
      2: "Used in 2 recipes",
      5: "Used in 5 recipes",
      22: "Used in 22 recipes",
    },
    pl: {
      0: "Używany w 0 przepisach",
      1: "Używany w 1 przepisie",
      2: "Używany w 2 przepisach",
      5: "Używany w 5 przepisach",
      22: "Używany w 22 przepisach",
    },
  };
  for (const lng of ["en", "pl"]) {
    for (const count of counts) {
      const got = i18next.t("ingredients.usedCount", { count, lng });
      const want = expected[lng][count];
      if (got !== want) {
        fail(
          `snapshot ${lng} count=${count}: got ${JSON.stringify(got)} want ${JSON.stringify(want)}`,
        );
      }
    }
  }
}

if (process.exitCode) {
  process.exit(process.exitCode);
}
console.log("i18n:check ok");
