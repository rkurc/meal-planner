import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api, ApiError } from "../api.js";

const IngredientDetail = () => {
  const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const [ingredient, setIngredient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) {
      setError(t("ingredients.invalid"));
      setLoading(false);
      return;
    }
    api
      .get(`/api/ingredients/${id}`)
      .then((data) => {
        setIngredient(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id, t]);

  const handleDelete = () => {
    if (
      !window.confirm(t("ingredients.deleteConfirm", { name: ingredient.name }))
    ) {
      return;
    }
    api
      .del(`/api/ingredients/${id}`)
      .then(() => {
        navigate("/ingredients");
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 409) {
          const usage =
            typeof err.body?.usage_count === "number"
              ? err.body.usage_count
              : ingredient.usage_count || 0;
          setError(t("ingredients.cannotDelete", { count: usage }));
          return;
        }
        setError(err.message);
      });
  };

  const backLink = (
    <Link
      to="/ingredients"
      className="text-blue-500 hover:text-blue-700 underline"
    >
      {t("ingredients.back")}
    </Link>
  );

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-gray-500">
          {t("ingredients.loadingOne")}
        </p>
      </div>
    );
  }

  if (error && !ingredient) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-red-500">
          {t("common.error", { message: error })}
        </p>
        <div className="text-center mt-4">{backLink}</div>
      </div>
    );
  }

  if (!ingredient) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-gray-500">{t("ingredients.notFound")}</p>
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
            <span className="text-gray-700 font-semibold">
              {t("ingredients.defaultUnitLabel")}{" "}
            </span>
            <span className="text-gray-600">{unit || "—"}</span>
          </div>
          <div>
            <span className="text-gray-700 font-semibold">
              {t("ingredients.locationLabel")}{" "}
            </span>
            <span className="text-gray-600">{location || "—"}</span>
          </div>
          <div>
            <span className="text-gray-700 font-semibold">
              {t("ingredients.usedInLabel")}{" "}
            </span>
            <span className="text-gray-600">
              {t("ingredients.usedCount", {
                count: ingredient.usage_count || 0,
              })}
            </span>
          </div>
        </div>

        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-3">
            {t("ingredients.recipesUsing")}
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
              {t("ingredients.noRecipesUsing")}
            </p>
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <Link
            to={`/ingredients/${id}/edit`}
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
          >
            {t("ingredients.edit")}
          </Link>
          <button
            type="button"
            onClick={handleDelete}
            className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded"
          >
            {t("ingredients.delete")}
          </button>
          <Link
            to="/ingredients"
            className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded"
          >
            {t("ingredients.back")}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default IngredientDetail;
