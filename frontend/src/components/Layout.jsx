import React from "react";
import { NavLink, Outlet } from "react-router-dom";

const Layout = () => {
  return (
    <div>
      <nav className="bg-gray-800 p-4">
        <div className="container mx-auto flex justify-between">
          <ul className="flex space-x-4">
            <li>
              <NavLink
                to="/recipes"
                className={({ isActive }) =>
                  isActive
                    ? "text-white bg-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    : "text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                }
              >
                Recipes
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/meal-plans"
                className={({ isActive }) =>
                  isActive
                    ? "text-white bg-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    : "text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                }
              >
                Meal Plans
              </NavLink>
            </li>
          </ul>
        </div>
      </nav>
      <main className="container mx-auto p-4">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
