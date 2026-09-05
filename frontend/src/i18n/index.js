import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import en from "./locales/en/common.json";
import pl from "./locales/pl/common.json";
import { STORAGE_KEY, SUPPORTED } from "./config";

function applyDocumentLocale(lng) {
  const short = (lng || "en").split("-")[0].toLowerCase();
  const resolved = SUPPORTED.includes(short) ? short : "en";
  document.documentElement.lang = resolved;
  document.title = i18n.t("app.title");
}

export const i18nReady = i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { common: en },
      pl: { common: pl },
    },
    fallbackLng: "en",
    supportedLngs: SUPPORTED,
    load: "languageOnly",
    nonExplicitSupportedLngs: true,
    ns: ["common"],
    defaultNS: "common",
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
      lookupLocalStorage: STORAGE_KEY,
    },
  })
  .then(() => applyDocumentLocale(i18n.resolvedLanguage));

i18n.on("languageChanged", applyDocumentLocale);

export default i18n;
