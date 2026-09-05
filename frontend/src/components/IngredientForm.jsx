import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

const IngredientForm = () => {
  const { t } = useTranslation();
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [formData, setFormData] = useState({
    name: "",
    default_unit: "",
    location: "",
  });
  const [knownLocations, setKnownLocations] = useState([]);
  const [loading, setLoading] = useState(isEditing);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isEditing) {
      return;
    }
    fetch(`/api/ingredients/${id}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(t("ingredients.notFound"));
        }
        return response.json();
      })
      .then((data) => {
        setFormData({
          name: data.name || "",
          default_unit: data.default_unit || data.unit || "",
          location: data.location || "",
        });
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id, isEditing, t]);

  useEffect(() => {
    fetch("/api/locations")
      .then((response) => {
        if (!response.ok) return [];
        return response.json();
      })
      .then((data) => {
        if (Array.isArray(data)) {
          setKnownLocations(data);
        }
      })
      .catch(() => {
        // non-fatal for suggestions
      });
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setError(t("ingredients.nameRequired"));
      return;
    }

    const payload = {
      name: formData.name.trim(),
      default_unit: formData.default_unit.trim(),
      location: formData.location.trim(),
    };
    const url = isEditing ? `/api/ingredients/${id}` : "/api/ingredients";
    const method = isEditing ? "PUT" : "POST";

    fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then(async (response) => {
        const data = await response.json().catch(() => ({}));
        if (response.status === 409) {
          throw new Error(data.error || t("ingredients.duplicateName"));
        }
        if (!response.ok) {
          throw new Error(data.error || t("ingredients.failedSave"));
        }
        return data;
      })
      .then((data) => {
        navigate(`/ingredients/${data.id}`);
      })
      .catch((err) => {
        setError(err.message);
      });
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-gray-500">{t("common.loading")}</p>
      </div>
    );
  }

  if (error && isEditing && !formData.name) {
    return (
      <div className="container mx-auto p-4">
        <p className="text-center text-red-500">
          {t("common.error", { message: error })}
        </p>
        <div className="text-center mt-4">
          <Link
            to="/ingredients"
            className="text-blue-500 hover:text-blue-700 underline"
          >
            {t("ingredients.back")}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          {isEditing
            ? t("ingredients.editTitle")
            : t("ingredients.createTitle")}
        </h1>

        {error && (
          <p className="mb-4 text-red-600 bg-red-50 border border-red-200 rounded p-3">
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              htmlFor="name"
              className="block text-gray-700 font-semibold mb-2"
            >
              {t("ingredients.name")}{" "}
              <span className="text-red-500">{t("common.required")}</span>
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

          <div className="mb-4">
            <label
              htmlFor="default_unit"
              className="block text-gray-700 font-semibold mb-2"
            >
              {t("ingredients.defaultUnit")}
            </label>
            <input
              type="text"
              id="default_unit"
              name="default_unit"
              value={formData.default_unit}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={t("ingredients.unitPlaceholder")}
            />
          </div>

          <div className="mb-6">
            <label
              htmlFor="location"
              className="block text-gray-700 font-semibold mb-2"
            >
              {t("ingredients.location")}
            </label>
            <input
              type="text"
              id="location"
              name="location"
              value={formData.location}
              onChange={handleInputChange}
              list="known-locations"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={t("ingredients.locationPlaceholder")}
            />
            <datalist id="known-locations">
              {knownLocations.map((loc) => (
                <option key={loc} value={loc} />
              ))}
            </datalist>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-6 rounded"
            >
              {isEditing
                ? t("ingredients.updateSubmit")
                : t("ingredients.createSubmit")}
            </button>
            <Link
              to={isEditing ? `/ingredients/${id}` : "/ingredients"}
              className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded"
            >
              {t("common.cancel")}
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default IngredientForm;
