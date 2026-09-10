import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";
import {
  OTHER_LOCATION_GROUP,
  formatItemLabel,
  formatSourceRecipeNames,
  groupItemsByLocation,
} from "../shoppingListGroups";

const ShoppingListView = ({ mealPlanId }) => {
  const { t, i18n } = useTranslation();
  const [shoppingList, setShoppingList] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editedItems, setEditedItems] = useState([]);

  const [knownIngredients, setKnownIngredients] = useState([]);
  const [knownLocations, setKnownLocations] = useState([]);
  const [knownUnits, setKnownUnits] = useState([]);
  const [ingredientDefaultUnits, setIngredientDefaultUnits] = useState({});

  useEffect(() => {
    setLoading(true);
    if (!mealPlanId) {
      setLoading(false);
      return;
    }
    fetch("/api/shopping-lists")
      .then((response) => response.json())
      .then((lists) => {
        const existing = lists.find((list) => list.meal_plan_id === mealPlanId);
        if (existing) {
          setShoppingList(existing);
          setEditedItems(existing.items || []);
        } else {
          setShoppingList(null);
          setEditedItems([]);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [mealPlanId]);

  useEffect(() => {
    // Fetch known ingredients and locations for suggestions (like in RecipeForm)
    fetch("/api/ingredients")
      .then((response) => {
        if (!response.ok) return [];
        return response.json();
      })
      .then((data) => {
        if (Array.isArray(data)) {
          setKnownIngredients(data);
        }
      })
      .catch(() => {
        // non-fatal
      });

    // Fetch richer summary data to support default unit auto-populate (name -> unit)
    // Follows exact existing pattern of separate fetch + non-fatal catch for known data.
    fetch("/api/ingredients/summary")
      .then((response) => {
        if (!response.ok) return [];
        return response.json();
      })
      .then((data) => {
        if (Array.isArray(data)) {
          const map = {};
          data.forEach((item) => {
            if (item && item.name) {
              map[item.name] = item.unit || "";
            }
          });
          setIngredientDefaultUnits(map);
        }
      })
      .catch(() => {
        // non-fatal
      });

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
        // non-fatal
      });

    fetch("/api/units")
      .then((response) => {
        if (!response.ok) return [];
        return response.json();
      })
      .then((data) => {
        if (Array.isArray(data)) {
          setKnownUnits(data);
        }
      })
      .catch(() => {
        // non-fatal
      });
  }, []);

  const handleGenerateList = () => {
    if (!mealPlanId) return;
    setLoading(true);
    fetch("/api/shopping-lists", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ meal_plan_id: mealPlanId }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to generate shopping list");
        }
        return response.json();
      })
      .then((data) => {
        setShoppingList(data);
        setEditedItems(data.items || []);
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  };

  const handleDeleteList = (listId) => {
    if (!window.confirm(t("shopping.deleteConfirm"))) {
      return;
    }
    fetch(`/api/shopping-lists/${listId}`, {
      method: "DELETE",
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to delete shopping list");
        }
        if (shoppingList && shoppingList.id === listId) {
          setShoppingList(null);
          setEditedItems([]);
          setEditMode(false);
        }
      })
      .catch((error) => {
        alert(`Error deleting shopping list: ${error.message}`);
      });
  };

  const handleItemChange = (index, field, value) => {
    const updated = [...editedItems];
    const currentUnit = updated[index].unit;
    updated[index][field] = value;
    // Auto-populate unit with ingredient's default (from summary) ONLY if unit field is currently empty/falsy.
    // This supports "when adding an ingredient" UX; does not overwrite if user already entered/changed unit.
    if (
      field === "name" &&
      value &&
      (!currentUnit || currentUnit.trim() === "")
    ) {
      const trimmedName = value.trim();
      const defUnit = ingredientDefaultUnits[trimmedName];
      if (defUnit) {
        updated[index].unit = defUnit;
      }
    }
    setEditedItems(updated);
  };

  const handleTogglePurchased = (index) => {
    const updated = [...editedItems];
    updated[index].purchased = !updated[index].purchased;
    setEditedItems(updated);
  };

  const handleAddItem = () => {
    setEditedItems([
      ...editedItems,
      {
        name: "",
        quantity: "",
        unit: "",
        location: "",
        purchased: false,
        source_recipe_names: [],
      },
    ]);
  };

  const handleRemoveItem = (index) => {
    const updated = editedItems.filter((_, i) => i !== index);
    setEditedItems(updated);
  };

  const handleSave = () => {
    if (!shoppingList) return;

    fetch(`/api/shopping-lists/${shoppingList.id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: shoppingList.name,
        items: editedItems,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to save shopping list");
        }
        return response.json();
      })
      .then((data) => {
        setShoppingList(data);
        setEditMode(false);
        alert(t("shopping.saved"));
      })
      .catch((error) => {
        alert(`Error saving shopping list: ${error.message}`);
      });
  };

  if (loading) {
    return <p className="text-gray-500">{t("shopping.loading")}</p>;
  }

  if (error) {
    return <p className="text-red-500">Error: {error}</p>;
  }

  if (!shoppingList) {
    return (
      <div className="bg-white shadow-md rounded-lg p-6 mt-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          {t("shopping.heading")}
        </h2>
        <p className="text-gray-600 mb-4">{t("shopping.noListForPlan")}</p>
        {mealPlanId && (
          <button
            onClick={handleGenerateList}
            data-testid="shopping-generate"
            className="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded"
          >
            {t("shopping.generate")}
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white shadow-md rounded-lg p-6 mt-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-gray-800">
          {t("shopping.listTitle", { name: shoppingList.name })}
        </h2>
        <div className="flex gap-2">
          {!editMode ? (
            <>
              <button
                onClick={() => setEditMode(true)}
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
              >
                {t("common.edit")}
              </button>
              <a
                href={`/shopping-lists/${shoppingList.id}/pdf?lang=${i18n.resolvedLanguage || "en"}`}
                data-testid="shopping-pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded inline-block"
              >
                {t("shopping.downloadPdf")}
              </a>
              <button
                onClick={() => handleDeleteList(shoppingList.id)}
                data-testid="shopping-delete"
                className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded"
              >
                {t("common.delete")}
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handleSave}
                className="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded"
              >
                {t("common.save")}
              </button>
              <button
                onClick={() => {
                  setEditedItems(shoppingList.items || []);
                  setEditMode(false);
                }}
                className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded"
              >
                {t("common.cancel")}
              </button>
            </>
          )}
        </div>
      </div>

      {editMode ? (
        <div>
          <div className="mb-4">
            {groupItemsByLocation(editedItems).map((group, groupIndex) => (
              <React.Fragment key={group.location}>
                <h3
                  className={`text-lg font-semibold text-gray-700 mb-2 border-b border-gray-200 pb-1 ${
                    groupIndex === 0 ? "" : "mt-4"
                  }`}
                >
                  {group.location === OTHER_LOCATION_GROUP
                    ? t("shopping.otherLocation")
                    : group.location}
                </h3>
                {group.entries.map(({ item, index }) => (
                  <div key={index} className="flex gap-2 items-center mb-2">
                    <input
                      type="text"
                      placeholder={t("shopping.itemName")}
                      value={item.name}
                      onChange={(e) =>
                        handleItemChange(index, "name", e.target.value)
                      }
                      list="known-ingredients"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder={t("shopping.qty")}
                      value={item.quantity}
                      onChange={(e) =>
                        handleItemChange(index, "quantity", e.target.value)
                      }
                      className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder={t("shopping.unit")}
                      value={item.unit}
                      onChange={(e) =>
                        handleItemChange(index, "unit", e.target.value)
                      }
                      list="known-units"
                      className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="text"
                      placeholder={t("shopping.location")}
                      value={item.location || ""}
                      onChange={(e) =>
                        handleItemChange(index, "location", e.target.value)
                      }
                      list="known-locations"
                      className="w-28 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      title={t("shopping.locationTitle")}
                    />
                    <button
                      onClick={() => handleRemoveItem(index)}
                      className="bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded"
                    >
                      {t("common.remove")}
                    </button>
                  </div>
                ))}
              </React.Fragment>
            ))}
          </div>
          <button
            onClick={handleAddItem}
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
          >
            {t("shopping.addItem")}
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
      ) : (
        <div className="space-y-4">
          {groupItemsByLocation(editedItems).map((group) => (
            <div key={group.location}>
              <h3 className="text-lg font-semibold text-gray-700 mb-2 border-b border-gray-200 pb-1">
                {group.location === OTHER_LOCATION_GROUP
                  ? t("shopping.otherLocation")
                  : group.location}
              </h3>
              <ul className="space-y-2">
                {group.entries.map(({ item, index }) => {
                  const sourceTitle = formatSourceRecipeNames(
                    item.source_recipe_names,
                  );
                  return (
                    <li
                      key={index}
                      className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={item.purchased || false}
                        onChange={() => handleTogglePurchased(index)}
                        className="w-5 h-5 cursor-pointer"
                      />
                      <span
                        className={`flex-1 ${item.purchased ? "line-through text-gray-400" : "text-gray-800"}`}
                        title={sourceTitle || undefined}
                        data-testid={
                          sourceTitle ? "shopping-item-sources" : undefined
                        }
                      >
                        {formatItemLabel(item)}
                      </span>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

ShoppingListView.propTypes = {
  mealPlanId: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  mealPlanName: PropTypes.string,
};

export default ShoppingListView;
