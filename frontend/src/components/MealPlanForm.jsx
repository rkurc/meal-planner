import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

const MealPlanForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    recipe_ids: [],
  });
  const [allRecipes, setAllRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRecipes = axios.get("/api/recipes");
    const fetchMealPlan = id ? axios.get(`/api/meal-plans/${id}`) : null;

    Promise.all([fetchRecipes, fetchMealPlan])
      .then(([recipesResponse, mealPlanResponse]) => {
        setAllRecipes(recipesResponse.data);
        if (mealPlanResponse) {
          const { name, description, recipes } = mealPlanResponse.data;
          setFormData({
            name,
            description,
            recipe_ids: recipes.map((r) => r.id),
          });
        }
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleRecipeChange = (e) => {
    const { value, checked } = e.target;
    const recipeId = parseInt(value, 10);
    setFormData((prev) => {
      const newRecipeIds = checked
        ? [...prev.recipe_ids, recipeId]
        : prev.recipe_ids.filter((id) => id !== recipeId);
      return { ...prev, recipe_ids: newRecipeIds };
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const apiCall = id
      ? axios.put(`/api/meal-plans/${id}`, formData)
      : axios.post("/api/meal-plans", formData);

    apiCall
      .then((response) => {
        navigate(`/meal-plans/${response.data.id}`);
      })
      .catch((error) => {
        setError(error.response?.data?.detail || error.message);
      });
  };

  if (loading) {
    return <p className="text-center text-gray-500">Loading form...</p>;
  }

  if (error) {
    return (
      <p className="text-center text-red-500">Error loading form: {error}</p>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-3xl font-bold text-gray-800 mb-6">
        {id ? "Edit Meal Plan" : "Create Meal Plan"}
      </h2>
      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-md rounded-lg p-6"
      >
        <div className="mb-4">
          <label
            htmlFor="name"
            className="block text-gray-700 font-bold mb-2"
          >
            Name
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>
        <div className="mb-4">
          <label
            htmlFor="description"
            className="block text-gray-700 font-bold mb-2"
          >
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700 font-bold mb-2">
            Recipes
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {allRecipes.map((recipe) => (
              <div key={recipe.id} className="flex items-center">
                <input
                  type="checkbox"
                  id={`recipe-${recipe.id}`}
                  value={recipe.id}
                  checked={formData.recipe_ids.includes(recipe.id)}
                  onChange={handleRecipeChange}
                  className="mr-2"
                />
                <label htmlFor={`recipe-${recipe.id}`}>{recipe.name}</label>
              </div>
            ))}
          </div>
        </div>
        <div className="flex items-center justify-between">
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          >
            {id ? "Update" : "Create"}
          </button>
          <button
            type="button"
            onClick={() => navigate(id ? `/meal-plans/${id}` : "/meal-plans")}
            className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default MealPlanForm;
