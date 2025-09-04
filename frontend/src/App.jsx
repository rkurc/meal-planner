import React from "react";
import {
  createBrowserRouter,
  RouterProvider,
  Navigate,
} from "react-router-dom";
import Layout from "./components/Layout";
import RecipeList from "./components/RecipeList";
import MealPlanList from "./components/MealPlanList";
import MealPlanDetail from "./components/MealPlanDetail";
import MealPlanForm from "./components/MealPlanForm";

const router = createBrowserRouter(
  [
    {
      path: "/",
      element: <Layout />,
      children: [
        {
          path: "/",
          element: <Navigate to="/recipes" replace />,
        },
        {
          path: "recipes",
          element: <RecipeList />,
        },
        {
          path: "meal-plans",
          element: <MealPlanList />,
        },
        {
          path: "meal-plans/new",
          element: <MealPlanForm />,
        },
        {
          path: "meal-plans/:id",
          element: <MealPlanDetail />,
        },
        {
          path: "meal-plans/:id/edit",
          element: <MealPlanForm />,
        },
      ],
    },
  ],
  {
    basename: "/static/react_app",
  },
);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
