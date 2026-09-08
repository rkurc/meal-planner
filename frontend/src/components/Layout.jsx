import React, { useEffect } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import LocaleSwitcher from "./LocaleSwitcher";

const navClass = ({ isActive }) =>
  isActive
    ? "text-white bg-gray-900 px-3 py-2 rounded-md text-sm font-medium"
    : "text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium";

const Layout = () => {
  const { t, i18n } = useTranslation();

  useEffect(() => {
    const short = (i18n.resolvedLanguage || "en").split("-")[0];
    document.documentElement.lang = short;
    document.title = t("app.title");
  }, [i18n.resolvedLanguage, t]);

  return (
    <div>
      <nav className="bg-gray-800 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <ul className="flex space-x-4">
            <li>
              <NavLink
                to="/recipes"
                data-testid="nav-recipes"
                className={navClass}
              >
                {t("nav.recipes")}
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/ingredients"
                data-testid="nav-ingredients"
                className={navClass}
              >
                {t("nav.ingredients")}
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/meal-plans"
                data-testid="nav-meal-plans"
                className={navClass}
              >
                {t("nav.mealPlans")}
              </NavLink>
            </li>
          </ul>
          <LocaleSwitcher />
        </div>
      </nav>
      <main className="container mx-auto p-4">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
