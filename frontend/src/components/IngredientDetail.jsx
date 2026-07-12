import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";

const IngredientDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [ingredient, setIngredient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const ingredientName = decodeURIComponent(id || "");

  useEffect(() => {
    if (!ingredientName) {
      setError("Invalid ingredient name");
      setLoading(false);
      return;
    }
    fetch(`/api/ingredients/info?name=${encodeURIComponent(ingredientName)}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Ingredient not found");
        }
        return response.json();
      })
      .then((data) => {
        setIngredient(data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  }, [id, ingredientName]);

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-gray-500">Loading ingredient...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-red-500">Error: {error}</p>
        <div className="text-center mt-4">
          <Link
            to="/ingredients"
            className="text-blue-500 hover:text-blue-700 underline"
          >
            Back to Ingredients
          </Link>
        </div>
      </div>
    );
  }

  if (!ingredient) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-gray-500">Ingredient not found.</p>
        <div className="text-center mt-4">
          <Link
            to="/ingredients"
            className="text-blue-500 hover:text-blue-700 underline"
          >
            Back to Ingredients
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          {ingredient.name}
        </h1>

        <div className="mb-4">
          <span className="text-gray-700 font-semibold">Used in: </span>
          <span className="text-gray-600">
            {ingredient.usage_count} recipe
            {ingredient.usage_count !== 1 ? "s" : ""}
          </span>
        </div>

        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-3">
            Recipes using this ingredient
          </h2>
          {ingredient.recipes && ingredient.recipes.length > 0 ? (
            <ul className="list-disc list-inside space-y-1">
              {ingredient.recipes.map((recipe) => (
                <li key={recipe.id} className="text-gray-700">
                  <Link
                    to={`/recipes/${recipe.id}`}
                    className="text-blue-600 hover:underline hover:text-blue-800"
                  >
                    {recipe.name}
                  </Link>
                  {recipe.description && (
                    <span className="text-gray-500 text-sm ml-2">
                      — {recipe.description}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 italic">
              No recipes found using this ingredient.
            </p>
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <Link
            to={`/ingredients/${encodeURIComponent(ingredient.name)}/edit`}
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
          >
            Edit Ingredient
          </Link>
          <Link
            to="/ingredients"
            className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded"
          >
            Back to Ingredients
          </Link>
        </div>
        <p className="mt-4 text-xs text-gray-400 italic">
          Note: Ingredient details are derived from recipes. To change usage,
          edit the recipes.
        </p>
      </div>
    </div>
  );
};

export default IngredientDetail;
