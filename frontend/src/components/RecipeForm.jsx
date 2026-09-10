import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate, Link, useLocation } from "react-router-dom";
import { Trans, useTranslation } from "react-i18next";
import { hasPlaceholderInstructions } from "../hasPlaceholderInstructions";
import { formDataFromDraft } from "../recipeDraft";
import { applyDefaultUnit } from "../defaultUnit";
import { useCatalogLookups } from "../hooks/useCatalogLookups";
import { api } from "../api.js";
import IngredientLineFields from "./IngredientLineFields";

const RecipeForm = () => {
  const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const isEditing = Boolean(id);
  const instructionsRef = useRef(null);
  const didFocusInstructions = useRef(false);

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    source_url: "",
    instructions: "",
    ingredients: [{ name: "", quantity: "", unit: "", location: "" }],
  });

  const [loading, setLoading] = useState(isEditing);
  const [error, setError] = useState(null);
  const {
    knownIngredients,
    knownLocations,
    knownUnits,
    ingredientDefaultUnits,
  } = useCatalogLookups();

  useEffect(() => {
    if (isEditing) {
      api
        .get(`/api/recipes/${id}`)
        .then((data) => {
          setFormData({
            name: data.name || "",
            description: data.description || "",
            source_url: data.source_url || "",
            instructions: data.instructions || "",
            ingredients:
              data.ingredients && data.ingredients.length > 0
                ? data.ingredients.map((ing) => ({
                    ...ing,
                    location: ing.location || ing.location_id || "",
                  }))
                : [{ name: "", quantity: "", unit: "", location: "" }],
          });
          setLoading(false);
        })
        .catch((error) => {
          setError(error.message);
          setLoading(false);
        });
    }
  }, [id, isEditing]);

  useEffect(() => {
    if (isEditing) {
      return;
    }
    const mapped = formDataFromDraft(
      location.state ? location.state.draft : null,
    );
    if (mapped) {
      setFormData(mapped);
    }
  }, [isEditing, location.state]);

  useEffect(() => {
    if (loading || didFocusInstructions.current || !instructionsRef.current) {
      return;
    }
    const wantsFocus =
      location.hash === "#instructions" ||
      (isEditing && hasPlaceholderInstructions(formData.instructions));
    if (wantsFocus) {
      instructionsRef.current.focus();
      instructionsRef.current.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
      didFocusInstructions.current = true;
    }
  }, [loading, location.hash, isEditing, formData.instructions]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleIngredientChange = (index, field, value) => {
    setFormData((prev) => {
      const updatedIngredients = [...prev.ingredients];
      updatedIngredients[index] = applyDefaultUnit(
        updatedIngredients[index],
        field,
        value,
        ingredientDefaultUnits,
      );
      return { ...prev, ingredients: updatedIngredients };
    });
  };

  const addIngredient = () => {
    setFormData((prev) => ({
      ...prev,
      ingredients: [
        ...prev.ingredients,
        { name: "", quantity: "", unit: "", location: "" },
      ],
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
      alert(t("recipes.nameAndInstructionsRequired"));
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

    const save = isEditing
      ? api.put(`/api/recipes/${id}`, recipeData)
      : api.post("/api/recipes", recipeData);

    save
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
        <p className="text-center text-gray-500">{t("common.loading")}</p>
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
            {t("recipes.back")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          {isEditing ? t("recipes.editTitle") : t("recipes.createTitle")}
        </h1>

        <form onSubmit={handleSubmit}>
          {/* Recipe Name */}
          <div className="mb-4">
            <label
              htmlFor="name"
              className="block text-gray-700 font-semibold mb-2"
            >
              {t("recipes.name")} <span className="text-red-500">*</span>
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
              {t("recipes.description")}
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
              {t("recipes.sourceUrl")}
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
              {t("recipes.ingredients")}
            </label>
            {formData.ingredients.map((ingredient, index) => (
              <IngredientLineFields
                key={index}
                item={ingredient}
                onChange={(field, value) =>
                  handleIngredientChange(index, field, value)
                }
                onRemove={() => removeIngredient(index)}
                namePlaceholder={t("recipes.ingredientName")}
                quantityPlaceholder={t("recipes.quantity")}
                unitPlaceholder={t("recipes.unit")}
                locationPlaceholder={t("recipes.location")}
                locationTitle={t("recipes.locationTitle")}
                removeLabel={t("common.remove")}
                removeDisabled={formData.ingredients.length === 1}
                listIds={{
                  ingredients: "known-ingredients",
                  units: "known-units",
                  locations: "known-locations",
                }}
              />
            ))}
            <button
              type="button"
              onClick={addIngredient}
              className="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded mt-2"
            >
              {t("recipes.addIngredient")}
            </button>
            <datalist id="known-ingredients">
              {knownIngredients.map((name, i) => (
                <option key={i} value={name} />
              ))}
            </datalist>
            <datalist id="known-locations">
              {knownLocations.map((loc, i) => (
                <option key={i} value={loc} />
              ))}
            </datalist>
            <datalist id="known-units">
              {knownUnits.map((unit, i) => (
                <option key={i} value={unit} />
              ))}
            </datalist>
          </div>

          {/* Instructions */}
          <div className="mb-6">
            <label
              htmlFor="instructions"
              className="block text-gray-700 font-semibold mb-2"
            >
              {t("recipes.instructions")}{" "}
              <span className="text-red-500">*</span>
            </label>
            {isEditing && hasPlaceholderInstructions(formData.instructions) && (
              <p className="text-sm text-amber-800 mb-2">
                {formData.source_url ? (
                  <Trans
                    i18nKey="recipes.placeholderHintWithSource"
                    components={{
                      source: (
                        <a
                          href={formData.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="underline"
                        />
                      ),
                    }}
                  />
                ) : (
                  t("recipes.placeholderHint")
                )}
              </p>
            )}
            <textarea
              id="instructions"
              name="instructions"
              ref={instructionsRef}
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
              {isEditing
                ? t("recipes.updateSubmit")
                : t("recipes.createSubmit")}
            </button>
            <Link
              to={isEditing ? `/recipes/${id}` : "/recipes"}
              className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-6 rounded inline-block"
            >
              {t("common.cancel")}
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RecipeForm;
