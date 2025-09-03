// frontend/src/components/RecipeItem.jsx
import React from "react";
import PropTypes from "prop-types";

const RecipeItem = ({ recipe }) => {
  return (
    <li className="p-4 mb-2 border rounded-lg shadow-sm hover:bg-gray-50">
      <h3 className="text-xl font-semibold text-blue-700">{recipe.name}</h3>
      {recipe.description && (
        <p className="text-gray-600 mt-1">{recipe.description}</p>
      )}
      {/* Add more details or links as needed */}
    </li>
  );
};

RecipeItem.propTypes = {
  recipe: PropTypes.shape({
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
  }).isRequired,
};

export default RecipeItem;
