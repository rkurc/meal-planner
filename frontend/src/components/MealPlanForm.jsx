import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

const MealPlanForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    recipes: [], // now [{recipe_id: str, count: number}, ...] supporting fractions
  });
  const [allRecipes, setAllRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRecipes = axios.get("/api/recipes");
    const fetches = [fetchRecipes];
    if (id) {
      fetches.push(axios.get(`/api/meal-plans/${id}`));
    }

    Promise.all(fetches)
      .then(([recipesResponse, mealPlanResponse]) => {
        setAllRecipes(recipesResponse.data);
        if (mealPlanResponse) {
          const data = mealPlanResponse.data;
          let loadedRecipes = [];
          if (Array.isArray(data.recipes)) {
            loadedRecipes = data.recipes
              .map((r) => ({
                recipe_id: r.id || r.recipe_id,
                count:
                  typeof r.count === "number"
                    ? r.count
                    : parseFloat(r.count) || 1,
              }))
              .filter((r) => r.recipe_id);
          } else if (Array.isArray(data.recipe_ids)) {
            // graceful support for old format
            loadedRecipes = data.recipe_ids.map((rid) => ({
              recipe_id: rid,
              count: 1,
            }));
          }
          setFormData({
            name: data.name || "",
            description: data.description || "",
            recipes: loadedRecipes,
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

  const addRecipeRow = () => {
    // Add a new row; prefer a recipe not yet selected
    const usedIds = new Set(formData.recipes.map((r) => r.recipe_id));
    const available =
      allRecipes.find((r) => !usedIds.has(r.id)) || allRecipes[0];
    const newRow = {
      recipe_id: available ? available.id : "",
      count: 1,
    };
    setFormData((prev) => ({
      ...prev,
      recipes: [...prev.recipes, newRow],
    }));
  };

  const updateRecipeRow = (index, field, value) => {
    setFormData((prev) => {
      const updated = [...prev.recipes];
      if (field === "recipe_id") {
        updated[index] = { ...updated[index], recipe_id: value };
      } else if (field === "count") {
        // accept any decimal, default to 0 if invalid
        const num = parseFloat(value);
        updated[index] = { ...updated[index], count: isNaN(num) ? 0 : num };
      }
      return { ...prev, recipes: updated };
    });
  };

  const removeRecipeRow = (index) => {
    setFormData((prev) => ({
      ...prev,
      recipes: prev.recipes.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Send new structure; include legacy recipe_ids for maximum compat if needed
    const recipesPayload = formData.recipes
      .filter((r) => r.recipe_id)
      .map((r) => ({
        id: r.recipe_id,
        count: parseFloat(r.count) || 1,
      }));
    const submitData = {
      name: formData.name,
      description: formData.description,
      recipes: recipesPayload,
      // recipe_ids kept for old consumers if desired
      recipe_ids: recipesPayload.map((r) => r.id),
    };
    const apiCall = id
      ? axios.put(`/api/meal-plans/${id}`, submitData)
      : axios.post("/api/meal-plans", submitData);

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
          <label htmlFor="name" className="block text-gray-700 font-bold mb-2">
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
          <label className="block text-gray-700 font-bold mb-2">Recipes</label>
          <div className="space-y-3 mb-3">
            {formData.recipes.length === 0 && (
              <p className="text-sm text-gray-500">
                No recipes added yet. Click below to add.
              </p>
            )}
            {formData.recipes.map((item, index) => (
              <div
                key={index}
                className="flex flex-col sm:flex-row items-start sm:items-center gap-2 border rounded p-3 bg-gray-50"
              >
                <select
                  value={item.recipe_id}
                  onChange={(e) =>
                    updateRecipeRow(index, "recipe_id", e.target.value)
                  }
                  className="flex-1 shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                >
                  <option value="">-- Select a recipe --</option>
                  {allRecipes.map((recipe) => (
                    <option key={recipe.id} value={recipe.id}>
                      {recipe.name}
                    </option>
                  ))}
                </select>
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-600 whitespace-nowrap">
                    Times:
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    value={item.count}
                    onChange={(e) =>
                      updateRecipeRow(index, "count", e.target.value)
                    }
                    className="w-24 shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => removeRecipeRow(index)}
                  className="bg-red-500 hover:bg-red-700 text-white text-sm font-bold py-1 px-3 rounded"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={addRecipeRow}
            className="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-3 rounded text-sm"
          >
            + Add Recipe
          </button>
          <p className="text-xs text-gray-500 mt-1">
            Use decimals for fractions e.g. 0.5, 1.25. Each row selects a recipe
            and its multiplier.
          </p>
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
