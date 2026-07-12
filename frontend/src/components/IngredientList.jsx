// frontend/src/components/IngredientList.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";

const IngredientList = () => {
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/ingredients/summary") // richer data for list with usage counts
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        setIngredients(data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <p className="text-center text-gray-500">Loading ingredients...</p>;
  }

  if (error) {
    return (
      <p className="text-center text-red-500">
        Error loading ingredients: {error}
      </p>
    );
  }

  if (ingredients.length === 0) {
    return (
      <p className="text-center text-gray-500">
        No ingredients found. Ingredients are added via recipes.
      </p>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Ingredients</h2>
        <span className="text-sm text-gray-500">
          (derived from recipes — no master data yet)
        </span>
      </div>
      <ul className="space-y-4">
        {ingredients.map((ingredient) => (
          <li
            key={ingredient.name}
            className="bg-white shadow-md rounded-lg p-4 hover:shadow-lg transition-shadow"
          >
            <Link
              to={`/ingredients/${encodeURIComponent(ingredient.name)}`}
              className="block"
            >
              <h3 className="text-xl font-semibold text-gray-800 hover:text-blue-600 transition-colors">
                {ingredient.name}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Used in {ingredient.usage_count} recipe
                {ingredient.usage_count !== 1 ? "s" : ""}
                {ingredient.unit ? ` • default unit: ${ingredient.unit}` : ""}
                {ingredient.location ? ` • ${ingredient.location}` : ""}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default IngredientList;
