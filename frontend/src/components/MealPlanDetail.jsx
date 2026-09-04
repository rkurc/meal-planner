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
  const [recipesInPlan, setRecipesInPlan] = useState([]); // now [{recipe, count}, ...]

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

  useEffect(() => {
    const entries =
      (mealPlan && mealPlan.recipes) ||
      (mealPlan && mealPlan.recipe_ids
        ? mealPlan.recipe_ids.map((rid) => ({ id: rid, count: 1 }))
        : []);
    if (!mealPlan || !entries || entries.length === 0) {
      setRecipesInPlan([]);
      return;
    }
    // Fetch all recipes then filter (small dataset; keeps one request)
    axios
      .get("/api/recipes")
      .then((res) => {
        const byId = Object.fromEntries(res.data.map((r) => [r.id, r]));
        const resolved = entries
          .map((e) => {
            const rid = e.id || e.recipe_id;
            const rec = byId[rid];
            if (!rec) return null;
            const c =
              typeof e.count === "number" ? e.count : parseFloat(e.count) || 1;
            return { recipe: rec, count: c };
          })
          .filter(Boolean);
        setRecipesInPlan(resolved);
      })
      .catch(() => setRecipesInPlan([]));
  }, [mealPlan]);

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

  const backLink = (
    <Link
      to="/meal-plans"
      className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
    >
      Back to Meal Plans
    </Link>
  );

  if (loading) {
    return <p className="text-center text-gray-500">Loading meal plan...</p>;
  }

  if (error) {
    return (
      <div className="container mx-auto p-4 text-center">
        <p className="text-red-500 mb-4">Error loading meal plan: {error}</p>
        {backLink}
      </div>
    );
  }

  if (!mealPlan) {
    return (
      <div className="container mx-auto p-4 text-center">
        <p className="text-gray-500 mb-4">Meal plan not found.</p>
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

        <h3 className="text-2xl font-semibold text-gray-700 mb-4">Recipes</h3>
        {recipesInPlan.length > 0 ? (
          <ul className="space-y-2">
            {recipesInPlan.map(({ recipe, count }) => (
              <li
                key={recipe.id}
                className="bg-gray-100 p-3 rounded-md flex justify-between items-center"
              >
                <span className="font-medium">{recipe.name}</span>
                <span className="text-sm text-gray-600 font-mono">
                  x {count}
                </span>
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
          {backLink}
        </div>
      </div>

      {/* Shopping List Section */}
      <ShoppingListView mealPlanId={id} mealPlanName={mealPlan.name} />
    </div>
  );
};

export default MealPlanDetail;
