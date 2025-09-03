// frontend/src/components/RecipeList.jsx
import React, { useState, useEffect } from "react";
import RecipeItem from "./RecipeItem";

const RecipeList = () => {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/recipes") // Assuming Flask serves API at this path
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
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <p className="text-center text-gray-500">Loading recipes...</p>;
  }

  if (error) {
    return (
      <p className="text-center text-red-500">Error loading recipes: {error}</p>
    );
  }

  if (recipes.length === 0) {
    return <p className="text-center text-gray-500">No recipes found.</p>;
  }

  return (
    <div className="container mx-auto p-4">
      <h2 className="text-3xl font-bold text-center mb-6 text-gray-800">
        Recipe List (React)
      </h2>
      <ul className="space-y-4">
        {recipes.map((recipe) => (
          <RecipeItem key={recipe.id} recipe={recipe} />
        ))}
      </ul>
    </div>
  );
};

export default RecipeList;
