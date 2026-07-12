import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";

const IngredientForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [formData, setFormData] = useState({
    name: "",
    unit: "",
    location: "",
  });

  const [loading, setLoading] = useState(isEditing);
  const [error, setError] = useState(null);

  const ingredientNameFromParam = id ? decodeURIComponent(id) : "";

  useEffect(() => {
    if (isEditing && ingredientNameFromParam) {
      fetch(
        `/api/ingredients/info?name=${encodeURIComponent(ingredientNameFromParam)}`,
      )
        .then((response) => {
          if (!response.ok) {
            throw new Error("Ingredient not found");
          }
          return response.json();
        })
        .then((data) => {
          setFormData({
            name: data.name || ingredientNameFromParam,
            unit: "", // no stored default unit separate from recipes yet
            location: "",
          });
          setLoading(false);
        })
        .catch((error) => {
          setError(error.message);
          setLoading(false);
        });
    }
  }, [id, isEditing, ingredientNameFromParam]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validation
    if (!formData.name.trim()) {
      alert("Ingredient name is required.");
      return;
    }

    const trimmedName = formData.name.trim();

    // Since no first-class ingredient storage (ingredients live inside recipes),
    // we do not persist standalone ingredient records. The form matches recipe form
    // structure for future extension. For now we simulate and navigate.
    // (Creating here won't affect recipes until the name is used in a RecipeForm.)
    alert(
      isEditing
        ? `Edited ingredient info for "${trimmedName}" (note: changes are not persisted separately; edit recipes to update actual usage/unit/location).`
        : `Created placeholder for "${trimmedName}" (note: standalone ingredients are derived from recipes. Add it to a recipe via Recipe form to see it listed with usage).`,
    );

    // Navigate to the detail view for this ingredient name
    navigate(`/ingredients/${encodeURIComponent(trimmedName)}`);
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
            to="/ingredients"
            className="text-blue-500 hover:text-blue-700 underline"
          >
            Back to Ingredients
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          {isEditing ? "Edit Ingredient" : "Add New Ingredient"}
        </h1>

        <form onSubmit={handleSubmit}>
          {/* Ingredient Name */}
          <div className="mb-4">
            <label
              htmlFor="name"
              className="block text-gray-700 font-semibold mb-2"
            >
              Ingredient Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              readOnly={isEditing} // name is identity key; to "rename" would require recipe updates
            />
            {isEditing && (
              <p className="text-xs text-gray-500 mt-1">
                Name is the key (editing name not supported without updating all
                recipes).
              </p>
            )}
          </div>

          {/* Default Unit */}
          <div className="mb-4">
            <label
              htmlFor="unit"
              className="block text-gray-700 font-semibold mb-2"
            >
              Default Unit
            </label>
            <input
              type="text"
              id="unit"
              name="unit"
              value={formData.unit}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. cups, g, tbsp"
            />
          </div>

          {/* Location / Aisle */}
          <div className="mb-6">
            <label
              htmlFor="location"
              className="block text-gray-700 font-semibold mb-2"
            >
              Default Location
            </label>
            <input
              type="text"
              id="location"
              name="location"
              value={formData.location}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Pantry, Dairy, Produce"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-6 rounded"
            >
              {isEditing ? "Update Ingredient" : "Add Ingredient"}
            </button>
            <Link
              to={
                isEditing
                  ? `/ingredients/${encodeURIComponent(ingredientNameFromParam)}`
                  : "/ingredients"
              }
              className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-6 rounded inline-block"
            >
              Cancel
            </Link>
          </div>
        </form>

        <p className="mt-6 text-sm text-gray-500 italic">
          Ingredients are currently managed inside recipes. This form provides
          the UI matching RecipeForm. Submitting here does not create
          independent master data or modify recipes.
        </p>
      </div>
    </div>
  );
};

export default IngredientForm;
