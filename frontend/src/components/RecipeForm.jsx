import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";

const RecipeForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const isEditing = Boolean(id);

    const [formData, setFormData] = useState({
        name: "",
        description: "",
        source_url: "",
        instructions: "",
        ingredients: [{ name: "", quantity: "", unit: "" }],
    });

    const [loading, setLoading] = useState(isEditing);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (isEditing) {
            fetch(`/api/recipes/${id}`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Recipe not found");
                    }
                    return response.json();
                })
                .then((data) => {
                    setFormData({
                        name: data.name || "",
                        description: data.description || "",
                        source_url: data.source_url || "",
                        instructions: data.instructions || "",
                        ingredients:
                            data.ingredients && data.ingredients.length > 0
                                ? data.ingredients
                                : [{ name: "", quantity: "", unit: "" }],
                    });
                    setLoading(false);
                })
                .catch((error) => {
                    setError(error.message);
                    setLoading(false);
                });
        }
    }, [id, isEditing]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleIngredientChange = (index, field, value) => {
        const updatedIngredients = [...formData.ingredients];
        updatedIngredients[index][field] = value;
        setFormData((prev) => ({
            ...prev,
            ingredients: updatedIngredients,
        }));
    };

    const addIngredient = () => {
        setFormData((prev) => ({
            ...prev,
            ingredients: [...prev.ingredients, { name: "", quantity: "", unit: "" }],
        }));
    };

    const removeIngredient = (index) => {
        if (formData.ingredients.length > 1) {
            const updatedIngredients = formData.ingredients.filter(
                (_, i) => i !== index,
            );
            setFormData((prev) => ({
                ...prev,
                ingredients: updatedIngredients,
            }));
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        // Validation
        if (!formData.name.trim() || !formData.instructions.trim()) {
            alert("Recipe name and instructions are required.");
            return;
        }

        // Filter out empty ingredients
        const filteredIngredients = formData.ingredients.filter(
            (ing) => ing.name.trim() !== "",
        );

        const recipeData = {
            name: formData.name,
            description: formData.description,
            source_url: formData.source_url,
            instructions: formData.instructions,
            ingredients: filteredIngredients,
        };

        const url = isEditing ? `/api/recipes/${id}` : "/api/recipes";
        const method = isEditing ? "PUT" : "POST";

        fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(recipeData),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Failed to save recipe");
                }
                return response.json();
            })
            .then((data) => {
                navigate(`/recipes/${data.id}`);
            })
            .catch((error) => {
                alert(`Error saving recipe: ${error.message}`);
            });
    };

    if (loading) {
        return (
            <div className="container mx-auto p-4">
                <p className="text-center text-gray-500">Loading...</p>
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

    return (
        <div className="container mx-auto p-4 max-w-4xl">
            <div className="bg-white shadow-md rounded-lg p-6">
                <h1 className="text-3xl font-bold text-gray-800 mb-6">
                    {isEditing ? "Edit Recipe" : "Create New Recipe"}
                </h1>

                <form onSubmit={handleSubmit}>
                    {/* Recipe Name */}
                    <div className="mb-4">
                        <label
                            htmlFor="name"
                            className="block text-gray-700 font-semibold mb-2"
                        >
                            Recipe Name <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            value={formData.name}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        />
                    </div>

                    {/* Description */}
                    <div className="mb-4">
                        <label
                            htmlFor="description"
                            className="block text-gray-700 font-semibold mb-2"
                        >
                            Description
                        </label>
                        <textarea
                            id="description"
                            name="description"
                            value={formData.description}
                            onChange={handleInputChange}
                            rows="3"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        ></textarea>
                    </div>

                    {/* Source URL */}
                    <div className="mb-4">
                        <label
                            htmlFor="source_url"
                            className="block text-gray-700 font-semibold mb-2"
                        >
                            Source URL
                        </label>
                        <input
                            type="url"
                            id="source_url"
                            name="source_url"
                            value={formData.source_url}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="https://example.com/recipe"
                        />
                    </div>

                    {/* Ingredients */}
                    <div className="mb-4">
                        <label className="block text-gray-700 font-semibold mb-2">
                            Ingredients
                        </label>
                        {formData.ingredients.map((ingredient, index) => (
                            <div key={index} className="flex gap-2 mb-2">
                                <input
                                    type="text"
                                    placeholder="Ingredient name"
                                    value={ingredient.name}
                                    onChange={(e) =>
                                        handleIngredientChange(index, "name", e.target.value)
                                    }
                                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                                <input
                                    type="text"
                                    placeholder="Quantity"
                                    value={ingredient.quantity}
                                    onChange={(e) =>
                                        handleIngredientChange(index, "quantity", e.target.value)
                                    }
                                    className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                                <input
                                    type="text"
                                    placeholder="Unit"
                                    value={ingredient.unit}
                                    onChange={(e) =>
                                        handleIngredientChange(index, "unit", e.target.value)
                                    }
                                    className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                                <button
                                    type="button"
                                    onClick={() => removeIngredient(index)}
                                    className="bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded-md"
                                    disabled={formData.ingredients.length === 1}
                                >
                                    Remove
                                </button>
                            </div>
                        ))}
                        <button
                            type="button"
                            onClick={addIngredient}
                            className="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded mt-2"
                        >
                            Add Ingredient
                        </button>
                    </div>

                    {/* Instructions */}
                    <div className="mb-6">
                        <label
                            htmlFor="instructions"
                            className="block text-gray-700 font-semibold mb-2"
                        >
                            Instructions <span className="text-red-500">*</span>
                        </label>
                        <textarea
                            id="instructions"
                            name="instructions"
                            value={formData.instructions}
                            onChange={handleInputChange}
                            rows="8"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            required
                        ></textarea>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-3">
                        <button
                            type="submit"
                            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-6 rounded"
                        >
                            {isEditing ? "Update Recipe" : "Create Recipe"}
                        </button>
                        <Link
                            to={isEditing ? `/recipes/${id}` : "/recipes"}
                            className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-6 rounded inline-block"
                        >
                            Cancel
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default RecipeForm;
