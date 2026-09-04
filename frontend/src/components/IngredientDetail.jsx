import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";

const IngredientDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [ingredient, setIngredient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) {
      setError("Invalid ingredient");
      setLoading(false);
      return;
    }
    fetch(`/api/ingredients/${id}`)
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
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  const handleDelete = () => {
    if (
      !window.confirm(
        `Are you sure you want to delete "${ingredient.name}"? This action cannot be undone.`,
      )
    ) {
      return;
    }
    fetch(`/api/ingredients/${id}`, {
      method: "DELETE",
    })
      .then(async (response) => {
        if (response.status === 204) {
          navigate("/ingredients");
          return;
        }
        if (response.status === 409) {
          let usage = ingredient.usage_count || 0;
          try {
            const data = await response.json();
            if (typeof data.usage_count === "number") {
              usage = data.usage_count;
            }
          } catch {
            // Fall back to the already-loaded usage count.
          }
          setError(
            `Cannot delete: still used by ${usage} recipe${
              usage !== 1 ? "s" : ""
            }. Remove it from those recipes first.`,
          );
          return;
        }
        if (response.status === 404) {
          throw new Error("Ingredient not found");
        }
        throw new Error("Failed to delete ingredient");
      })
      .catch((err) => {
        setError(err.message);
      });
  };

  const backLink = (
    <Link
      to="/ingredients"
      className="text-blue-500 hover:text-blue-700 underline"
    >
      Back to Ingredients
    </Link>
  );

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-gray-500">Loading ingredient...</p>
      </div>
    );
  }

  if (error && !ingredient) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-red-500">Error: {error}</p>
        <div className="text-center mt-4">{backLink}</div>
      </div>
    );
  }

  if (!ingredient) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-gray-500">Ingredient not found.</p>
        <div className="text-center mt-4">{backLink}</div>
      </div>
    );
  }

  const unit = ingredient.default_unit || ingredient.unit || "";
  const location = ingredient.location || "";

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          {ingredient.name}
        </h1>

        {error && (
          <p className="mb-4 text-red-600 bg-red-50 border border-red-200 rounded p-3">
            {error}
          </p>
        )}

        <div className="mb-4 space-y-1">
          <div>
            <span className="text-gray-700 font-semibold">Default unit: </span>
            <span className="text-gray-600">{unit || "—"}</span>
          </div>
          <div>
            <span className="text-gray-700 font-semibold">Location: </span>
            <span className="text-gray-600">{location || "—"}</span>
          </div>
          <div>
            <span className="text-gray-700 font-semibold">Used in: </span>
            <span className="text-gray-600">
              {ingredient.usage_count} recipe
              {ingredient.usage_count !== 1 ? "s" : ""}
            </span>
          </div>
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
            to={`/ingredients/${id}/edit`}
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
          >
            Edit Ingredient
          </Link>
          <button
            type="button"
            onClick={handleDelete}
            className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded"
          >
            Delete Ingredient
          </button>
          <Link
            to="/ingredients"
            className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded"
          >
            Back to Ingredients
          </Link>
        </div>
      </div>
    </div>
  );
};

export default IngredientDetail;
