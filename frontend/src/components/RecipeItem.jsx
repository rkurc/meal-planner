// frontend/src/components/RecipeItem.jsx
import React from "react";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { hasPlaceholderInstructions } from "../hasPlaceholderInstructions";

const RecipeItem = ({ recipe }) => {
  const needsInstructions = hasPlaceholderInstructions(recipe.instructions);

  return (
    <li className="bg-white shadow-md rounded-lg p-4 hover:shadow-lg transition-shadow">
      <Link to={`/recipes/${recipe.id}`} className="block">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className="text-xl font-semibold text-gray-800 hover:text-blue-600 transition-colors">
            {recipe.name}
          </h3>
          {needsInstructions && (
            <span
              data-testid="needs-instructions-badge"
              className="inline-block text-xs font-medium text-amber-800 bg-amber-100 px-2 py-0.5 rounded"
            >
              Needs instructions
            </span>
          )}
        </div>
      </Link>
    </li>
  );
};

RecipeItem.propTypes = {
  recipe: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    name: PropTypes.string.isRequired,
    instructions: PropTypes.string,
  }).isRequired,
};

export default RecipeItem;
