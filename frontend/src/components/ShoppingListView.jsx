import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";
import {
  OTHER_LOCATION_GROUP,
  formatItemLabel,
  formatSourceRecipeNames,
  groupItemsByLocation,
} from "../shoppingListGroups";
import { applyDefaultUnit } from "../defaultUnit";
import { useCatalogLookups } from "../hooks/useCatalogLookups";
import IngredientLineFields from "./IngredientLineFields";

const ShoppingListView = ({ mealPlanId }) => {
  const { t, i18n } = useTranslation();
  const [shoppingList, setShoppingList] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editedItems, setEditedItems] = useState([]);
  const {
    knownIngredients,
    knownLocations,
    knownUnits,
    ingredientDefaultUnits,
  } = useCatalogLookups();

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
    setEditedItems((prev) => {
      const updated = [...prev];
      updated[index] = applyDefaultUnit(
        updated[index],
        field,
        value,
        ingredientDefaultUnits,
      );
      return updated;
    });
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
                  <IngredientLineFields
                    key={index}
                    item={item}
                    onChange={(field, value) =>
                      handleItemChange(index, field, value)
                    }
                    onRemove={() => handleRemoveItem(index)}
                    namePlaceholder={t("shopping.itemName")}
                    quantityPlaceholder={t("shopping.qty")}
                    unitPlaceholder={t("shopping.unit")}
                    locationPlaceholder={t("shopping.location")}
                    locationTitle={t("shopping.locationTitle")}
                    removeLabel={t("common.remove")}
                    listIds={{
                      ingredients: "known-ingredients",
                      units: "known-units",
                      locations: "known-locations",
                    }}
                  />
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
                      <span
                        className="flex-1 text-gray-800"
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
