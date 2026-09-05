import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import axios from "axios";

const MealPlanList = () => {
  const { t } = useTranslation();
  const [mealPlans, setMealPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get("/api/meal-plans")
      .then((response) => {
        setMealPlans(response.data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <p className="text-center text-gray-500">{t("mealPlans.loading")}</p>;
  }

  if (error) {
    return (
      <p className="text-center text-red-500">
        {t("mealPlans.errorLoad", { message: error })}
      </p>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">{t("mealPlans.title")}</h2>
        <Link
          to="/meal-plans/new"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          {t("mealPlans.new")}
        </Link>
      </div>
      {mealPlans.length === 0 ? (
        <p className="text-center text-gray-500">{t("mealPlans.empty")}</p>
      ) : (
        <ul className="space-y-4">
          {mealPlans.map((plan) => (
            <li
              key={plan.id}
              className="bg-white shadow-md rounded-lg p-4 flex justify-between items-center"
            >
              <Link
                to={`/meal-plans/${plan.id}`}
                className="text-xl font-semibold text-blue-600 hover:underline"
              >
                {plan.name}
              </Link>
              <span className="text-gray-600">{plan.description}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default MealPlanList;
