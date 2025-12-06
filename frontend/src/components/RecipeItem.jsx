// frontend/src/components/RecipeItem.jsx
import React from "react";
import { Link } from "react-router-dom";

const RecipeItem = ({ recipe }) => {
  return (
    <li className="bg-white shadow-md rounded-lg p-4 hover:shadow-lg transition-shadow">
      <Link to={`/recipes/${recipe.id}`} className="block">
        <h3 className="text-xl font-semibold text-gray-800 hover:text-blue-600 transition-colors">
          {recipe.name}
        </h3>
        {recipe.description && (
          <p className="text-gray-600 mt-2">{recipe.description}</p>
        )}
        {recipe.ingredients && recipe.ingredients.length > 0 && (
          <p className="text-sm text-gray-500 mt-2">
            {recipe.ingredients.length} ingredient
            {recipe.ingredients.length !== 1 ? "s" : ""}
          </p>
        )}
      </Link>
    </li>
  );
};

export default RecipeItem;
