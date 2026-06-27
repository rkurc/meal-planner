// frontend/src/components/RecipeItem.jsx
import React from "react";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";

const RecipeItem = ({ recipe }) => {
  return (
    <li className="bg-white shadow-md rounded-lg p-4 hover:shadow-lg transition-shadow">
      <Link to={`/recipes/${recipe.id}`} className="block">
        <h3 className="text-xl font-semibold text-gray-800 hover:text-blue-600 transition-colors">
          {recipe.name}
        </h3>
      </Link>
    </li>
  );
};

RecipeItem.propTypes = {
  recipe: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    name: PropTypes.string.isRequired,
  }).isRequired,
};

export default RecipeItem;
