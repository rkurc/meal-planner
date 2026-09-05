import React from "react";
import { useTranslation } from "react-i18next";
import { SUPPORTED } from "../i18n/config";

const LocaleSwitcher = () => {
  const { t, i18n } = useTranslation();
  const current = (i18n.resolvedLanguage || i18n.language || "en")
    .split("-")[0]
    .toLowerCase();

  return (
    <div
      className="flex items-center space-x-1"
      role="group"
      aria-label={t("nav.language")}
    >
      {SUPPORTED.map((lng) => {
        const pressed = current === lng;
        return (
          <button
            key={lng}
            type="button"
            data-testid={`locale-${lng}`}
            aria-pressed={pressed}
            aria-label={
              lng === "en" ? t("nav.languageEn") : t("nav.languagePl")
            }
            onClick={() => i18n.changeLanguage(lng)}
            className={
              pressed
                ? "text-white bg-gray-900 px-2 py-1 rounded text-xs font-medium"
                : "text-gray-300 hover:bg-gray-700 hover:text-white px-2 py-1 rounded text-xs font-medium"
            }
          >
            {lng === "en" ? t("nav.languageEn") : t("nav.languagePl")}
          </button>
        );
      })}
    </div>
  );
};

export default LocaleSwitcher;
