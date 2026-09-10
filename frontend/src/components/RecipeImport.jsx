import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

const RecipeImport = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [sourceUrl, setSourceUrl] = useState("");
  const [text, setText] = useState("");
  const [error, setError] = useState(null);
  const [parsing, setParsing] = useState(false);

  const errorFromResponse = async (response) => {
    let body = {};
    try {
      body = await response.json();
    } catch {
      body = {};
    }
    if (response.status === 503) {
      return t("recipes.importUnavailable");
    }
    if (response.status === 504) {
      return t("recipes.importTimeout");
    }
    if (response.status === 422) {
      return t("recipes.importUnusable");
    }
    return t("recipes.importError", {
      message: body.error || t("recipes.failedSave"),
    });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!text.trim()) {
      setError(t("recipes.importTextRequired"));
      return;
    }
    setParsing(true);
    setError(null);
    fetch("/api/recipes/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        source_url: sourceUrl.trim(),
      }),
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(await errorFromResponse(response));
        }
        return response.json();
      })
      .then((draft) => {
        navigate("/recipes/new", { state: { draft } });
      })
      .catch((err) => {
        setError(err.message);
        setParsing(false);
      });
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          {t("recipes.importTitle")}
        </h1>
        <p className="text-gray-600 mb-6">{t("recipes.importHint")}</p>

        {error && (
          <p
            className="text-red-600 mb-4"
            data-testid="recipes-import-error"
            role="alert"
          >
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit}>
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
              value={sourceUrl}
              onChange={(event) => setSourceUrl(event.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://example.com/recipe"
            />
          </div>

          <div className="mb-6">
            <label
              htmlFor="import-text"
              className="block text-gray-700 font-semibold mb-2"
            >
              {t("recipes.importText")} <span className="text-red-500">*</span>
            </label>
            <textarea
              id="import-text"
              name="text"
              value={text}
              onChange={(event) => setText(event.target.value)}
              rows="14"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              required
            ></textarea>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              data-testid="recipes-import-parse"
              disabled={parsing}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white font-semibold py-2 px-6 rounded"
            >
              {parsing ? t("recipes.importParsing") : t("recipes.importParse")}
            </button>
            <Link
              to="/recipes"
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

export default RecipeImport;
