import React from "react";
import {
  createBrowserRouter,
  RouterProvider,
  Navigate,
} from "react-router-dom";
import Layout from "./components/Layout";
import RecipeList from "./components/RecipeList";
import RecipeDetail from "./components/RecipeDetail";
import RecipeForm from "./components/RecipeForm";
import IngredientList from "./components/IngredientList";
import IngredientDetail from "./components/IngredientDetail";
import IngredientForm from "./components/IngredientForm";
import MealPlanList from "./components/MealPlanList";
import MealPlanDetail from "./components/MealPlanDetail";
import MealPlanForm from "./components/MealPlanForm";
import ShoppingListView from "./components/ShoppingListView";

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
          path: "recipes/new",
          element: <RecipeForm />,
        },
        {
          path: "recipes/:id",
          element: <RecipeDetail />,
        },
        {
          path: "recipes/:id/edit",
          element: <RecipeForm />,
        },
        {
          path: "ingredients",
          element: <IngredientList />,
        },
        {
          path: "ingredients/new",
          element: <IngredientForm />,
        },
        {
          path: "ingredients/:id",
          element: <IngredientDetail />,
        },
        {
          path: "ingredients/:id/edit",
          element: <IngredientForm />,
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
        {
          path: "shopping-lists",
          element: <ShoppingListView />,
        },
      ],
    },
  ],
  {
    basename: "/ui",
  },
);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
