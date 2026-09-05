import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { hasPlaceholderInstructions } from "../hasPlaceholderInstructions";

const RecipeDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/recipes/${id}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Recipe not found");
        }
        return response.json();
      })
      .then((data) => {
        setRecipe(data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  }, [id]);

  const handleDelete = () => {
    if (window.confirm(t("recipes.deleteConfirm", { name: recipe.name }))) {
      fetch(`/api/recipes/${id}`, {
        method: "DELETE",
      })
        .then((response) => {
          if (response.ok) {
            navigate("/recipes");
          } else {
            throw new Error("Failed to delete recipe");
          }
        })
        .catch((error) => {
          alert(`Error deleting recipe: ${error.message}`);
        });
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-gray-500">{t("recipes.loadingOne")}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-red-500">Error: {error}</p>
        <div className="text-center mt-4">
          <Link
            to="/recipes"
            className="text-blue-500 hover:text-blue-700 underline"
          >
            {t("recipes.back")}
          </Link>
        </div>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-gray-500">{t("recipes.notFound")}</p>
        <div className="text-center mt-4">
          <Link
            to="/recipes"
            className="text-blue-500 hover:text-blue-700 underline"
          >
            {t("recipes.back")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">{recipe.name}</h1>

        {recipe.description && (
          <p className="text-gray-600 mb-4">{recipe.description}</p>
        )}

        {recipe.source_url && (
          <div className="mb-4">
            <span className="text-gray-700 font-semibold">
              {t("recipes.source")}{" "}
            </span>
            <a
              href={recipe.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:text-blue-700 underline"
            >
              {recipe.source_url}
            </a>
          </div>
        )}

        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-3">
            {t("recipes.ingredients")}
          </h2>
          {recipe.ingredients && recipe.ingredients.length > 0 ? (
            <ul className="list-disc list-inside space-y-1">
              {recipe.ingredients.map((ingredient, index) => (
                <li key={index} className="text-gray-700">
                  {ingredient.quantity && ingredient.unit
                    ? `${ingredient.quantity} ${ingredient.unit} ${ingredient.name}`
                    : ingredient.quantity
                      ? `${ingredient.quantity} ${ingredient.name}`
                      : ingredient.name}
                  {ingredient.location
                    ? ` (${ingredient.location})`
                    : ingredient.location_id
                      ? ` (loc: ${ingredient.location_id})`
                      : ""}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 italic">{t("recipes.noIngredients")}</p>
          )}
        </div>

        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-3">
            {t("recipes.instructions")}
          </h2>
          {hasPlaceholderInstructions(recipe.instructions) ? (
            <div
              data-testid="missing-instructions-banner"
              role="status"
              className="rounded-md border border-amber-300 bg-amber-50 p-4"
            >
              <p className="font-semibold text-amber-900">
                {t("recipes.missingBannerTitle")}
              </p>
              <p className="text-amber-800 mt-1">
                {t("recipes.missingBannerBody")}
              </p>
              <div className="flex flex-wrap gap-3 mt-4">
                {recipe.source_url && (
                  <a
                    href={recipe.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-amber-600 hover:bg-amber-700 text-white font-semibold py-2 px-4 rounded"
                  >
                    {t("recipes.openSource")}
                  </a>
                )}
                <Link
                  to={`/recipes/${id}/edit#instructions`}
                  className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
                >
                  {t("recipes.editInstructions")}
                </Link>
              </div>
            </div>
          ) : (
            <div className="text-gray-700 whitespace-pre-wrap">
              {recipe.instructions}
            </div>
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <Link
            to={`/recipes/${id}/edit`}
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
          >
            {t("recipes.edit")}
          </Link>
          <button
            onClick={handleDelete}
            className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded"
          >
            {t("recipes.delete")}
          </button>
          <Link
            to="/recipes"
            className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded"
          >
            {t("recipes.back")}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RecipeDetail;
