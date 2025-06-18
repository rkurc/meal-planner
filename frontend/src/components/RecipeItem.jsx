// frontend/src/components/RecipeItem.jsx
import React from 'react';

const RecipeItem = ({ recipe }) => {
  return (
    <li className="p-4 mb-2 border rounded-lg shadow-sm hover:bg-gray-50">
      <h3 className="text-xl font-semibold text-blue-700">{recipe.name}</h3>
      {recipe.description && <p className="text-gray-600 mt-1">{recipe.description}</p>}
      {/* Add more details or links as needed */}
    </li>
  );
};

export default RecipeItem;
