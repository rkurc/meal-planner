import React, { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import RecipeItem from "./RecipeItem";

const RecipeList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const q = searchParams.get("q") || "";
  const ingredient = searchParams.get("ingredient") || "";
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [qInput, setQInput] = useState(q);
  const [ingredientInput, setIngredientInput] = useState(ingredient);

  useEffect(() => {
    setQInput(q);
    setIngredientInput(ingredient);
  }, [q, ingredient]);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (ingredient) params.set("ingredient", ingredient);
    const qs = params.toString();
    fetch(qs ? `/api/recipes?${qs}` : "/api/recipes")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        setRecipes(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [q, ingredient]);

  const handleSearch = (event) => {
    event.preventDefault();
    const next = {};
    if (qInput.trim()) next.q = qInput.trim();
    if (ingredientInput.trim()) next.ingredient = ingredientInput.trim();
    setSearchParams(next);
  };

  const handleClear = () => {
    setQInput("");
    setIngredientInput("");
    setSearchParams({});
  };

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Recipes</h2>
        <Link
          to="/recipes/new"
          className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
        >
          Create New Recipe
        </Link>
      </div>
      <form
        onSubmit={handleSearch}
        className="mb-6 flex flex-wrap items-center gap-2"
      >
        <input
          id="recipe-search"
          type="text"
          value={qInput}
          onChange={(e) => setQInput(e.target.value)}
          placeholder="Search term..."
          className="px-3 py-2 border border-gray-300 rounded-md shadow-sm w-64"
        />
        <input
          id="ingredient-filter"
          type="text"
          value={ingredientInput}
          onChange={(e) => setIngredientInput(e.target.value)}
          placeholder="Filter by ingredient..."
          className="px-3 py-2 border border-gray-300 rounded-md shadow-sm w-52"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Search
        </button>
        {(q || ingredient) && (
          <Link
            to="/recipes"
            onClick={handleClear}
            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
          >
            Clear
          </Link>
        )}
      </form>
      {loading && (
        <p className="text-center text-gray-500">Loading recipes...</p>
      )}
      {error && (
        <p className="text-center text-red-500">
          Error loading recipes: {error}
        </p>
      )}
      {!loading && !error && recipes.length === 0 && (
        <p className="text-center text-gray-500">No recipes found.</p>
      )}
      {!loading && !error && recipes.length > 0 && (
        <ul className="space-y-4">
          {recipes.map((recipe) => (
            <RecipeItem key={recipe.id} recipe={recipe} />
          ))}
        </ul>
      )}
    </div>
  );
};

export default RecipeList;
