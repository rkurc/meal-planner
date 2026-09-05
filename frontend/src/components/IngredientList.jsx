// frontend/src/components/IngredientList.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";

const IngredientList = () => {
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/ingredients/summary")
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
      .catch((err) => {
        setError(err.message);
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

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Ingredients</h2>
        <Link
          to="/ingredients/new"
          className="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded"
        >
          Add ingredient
        </Link>
      </div>
      {ingredients.length === 0 ? (
        <p className="text-center text-gray-500">
          No ingredients found. Add one to the catalog, or they will also appear
          when used in recipes.
        </p>
      ) : (
        <ul className="space-y-2">
          {ingredients.map((ingredient) => {
            const count = ingredient.usage_count || 0;
            const unit = ingredient.unit || ingredient.default_unit || "";
            const loc = ingredient.location || "";
            return (
              <li
                key={ingredient.id || ingredient.name}
                className="bg-white shadow-md rounded-lg p-3 flex justify-between items-center hover:shadow-lg transition-shadow"
              >
                <Link
                  to={`/ingredients/${ingredient.id}`}
                  className="text-xl font-semibold text-blue-600 hover:text-blue-800 hover:underline"
                >
                  {ingredient.name}
                </Link>
                <span className="text-sm text-gray-600">
                  Used in {count} recipe{count !== 1 ? "s" : ""}
                  {unit ? ` • unit: ${unit}` : ""}
                  {loc ? ` • ${loc}` : ""}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

export default IngredientList;
