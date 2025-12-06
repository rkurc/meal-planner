import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import ShoppingListView from "./ShoppingListView";

const MealPlanDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get(`/api/meal-plans/${id}`)
      .then((response) => {
        setMealPlan(response.data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  }, [id]);

  const handleDelete = () => {
    if (window.confirm("Are you sure you want to delete this meal plan?")) {
      axios
        .delete(`/api/meal-plans/${id}`)
        .then(() => {
          navigate("/meal-plans");
        })
        .catch((error) => {
          setError(error.message);
        });
    }
  };

  if (loading) {
    return <p className="text-center text-gray-500">Loading meal plan...</p>;
  }

  if (error) {
    return (
      <p className="text-center text-red-500">
        Error loading meal plan: {error}
      </p>
    );
  }

  if (!mealPlan) {
    return <p className="text-center text-gray-500">Meal plan not found.</p>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-4">
          {mealPlan.name}
        </h2>
        <p className="text-gray-600 mb-6">{mealPlan.description}</p>

        <h3 className="text-2xl font-semibold text-gray-700 mb-4">Recipes</h3>
        {mealPlan.recipes && mealPlan.recipes.length > 0 ? (
          <ul className="space-y-2">
            {mealPlan.recipes.map((recipe) => (
              <li key={recipe.id} className="bg-gray-100 p-3 rounded-md">
                <span className="font-medium">{recipe.name}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">No recipes in this meal plan.</p>
        )}

        <div className="mt-6 flex space-x-4">
          <Link
            to={`/meal-plans/${id}/edit`}
            className="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded"
          >
            Edit
          </Link>
          <button
            onClick={handleDelete}
            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Shopping List Section */}
      <ShoppingListView mealPlanId={id} mealPlanName={mealPlan.name} />
    </div>
  );
};

export default MealPlanDetail;
