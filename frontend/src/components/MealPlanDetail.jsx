import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { api } from "../api.js";
import ShoppingListView from "./ShoppingListView";

const MealPlanDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get(`/api/meal-plans/${id}`)
      .then((data) => {
        setMealPlan(data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  }, [id]);

  const handleDelete = () => {
    if (window.confirm(t("mealPlans.deleteConfirm"))) {
      api
        .del(`/api/meal-plans/${id}`)
        .then(() => {
          navigate("/meal-plans");
        })
        .catch((error) => {
          setError(error.message);
        });
    }
  };

  const backLink = (
    <Link
      to="/meal-plans"
      className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
    >
      {t("mealPlans.back")}
    </Link>
  );

  if (loading) {
    return (
      <p className="text-center text-gray-500">{t("mealPlans.loadingPlan")}</p>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4 text-center">
        <p className="text-red-500 mb-4">
          {t("mealPlans.errorLoadPlan", { message: error })}
        </p>
        {backLink}
      </div>
    );
  }

  if (!mealPlan) {
    return (
      <div className="container mx-auto p-4 text-center">
        <p className="text-gray-500 mb-4">{t("mealPlans.notFound")}</p>
        {backLink}
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-4">
          {mealPlan.name}
        </h2>
        <p className="text-gray-600 mb-6">{mealPlan.description}</p>

        <h3 className="text-2xl font-semibold text-gray-700 mb-4">
          {t("mealPlans.recipes")}
        </h3>
        {mealPlan.recipes && mealPlan.recipes.length > 0 ? (
          <ul className="space-y-2">
            {mealPlan.recipes.map(({ id: recipeId, name, count }) => (
              <li
                key={recipeId}
                className="bg-gray-100 p-3 rounded-md flex justify-between items-center"
              >
                <Link
                  to={`/recipes/${recipeId}`}
                  className="font-medium text-blue-600 hover:underline"
                >
                  {name}
                </Link>
                <span className="text-sm text-gray-600 font-mono">
                  x {count}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">{t("mealPlans.emptyRecipes")}</p>
        )}

        <div className="mt-6 flex space-x-4">
          <Link
            to={`/meal-plans/${id}/edit`}
            className="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded"
          >
            {t("common.edit")}
          </Link>
          <button
            onClick={handleDelete}
            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
          >
            {t("common.delete")}
          </button>
          {backLink}
        </div>
      </div>

      {/* Shopping List Section */}
      <ShoppingListView mealPlanId={id} mealPlanName={mealPlan.name} />
    </div>
  );
};

export default MealPlanDetail;
