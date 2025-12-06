import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";

const RecipeDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
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
        if (
            window.confirm(
                `Are you sure you want to delete "${recipe.name}"? This action cannot be undone.`,
            )
        ) {
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
                <p className="text-center text-gray-500">Loading recipe...</p>
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
                        Back to Recipes
                    </Link>
                </div>
            </div>
        );
    }

    if (!recipe) {
        return (
            <div className="container mx-auto p-4">
                <p className="text-center text-gray-500">Recipe not found.</p>
                <div className="text-center mt-4">
                    <Link
                        to="/recipes"
                        className="text-blue-500 hover:text-blue-700 underline"
                    >
                        Back to Recipes
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-4 max-w-4xl">
            <div className="bg-white shadow-md rounded-lg p-6">
                <h1 className="text-3xl font-bold text-gray-800 mb-4">
                    {recipe.name}
                </h1>

                {recipe.description && (
                    <p className="text-gray-600 mb-4">{recipe.description}</p>
                )}

                {recipe.source_url && (
                    <div className="mb-4">
                        <span className="text-gray-700 font-semibold">Source: </span>
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
                        Ingredients
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
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-500 italic">No ingredients listed.</p>
                    )}
                </div>

                <div className="mb-6">
                    <h2 className="text-2xl font-semibold text-gray-800 mb-3">
                        Instructions
                    </h2>
                    <div className="text-gray-700 whitespace-pre-wrap">
                        {recipe.instructions}
                    </div>
                </div>

                <div className="flex gap-3 mt-6">
                    <Link
                        to={`/recipes/${id}/edit`}
                        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
                    >
                        Edit Recipe
                    </Link>
                    <button
                        onClick={handleDelete}
                        className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded"
                    >
                        Delete Recipe
                    </button>
                    <Link
                        to="/recipes"
                        className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded"
                    >
                        Back to Recipes
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default RecipeDetail;
