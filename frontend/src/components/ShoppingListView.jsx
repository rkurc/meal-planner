import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

const ShoppingListView = ({
  mealPlanId,
  mealPlanName,
  shoppingListId: propShoppingListId,
}) => {
  const [shoppingList, setShoppingList] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editedItems, setEditedItems] = useState([]);

  const [knownIngredients, setKnownIngredients] = useState([]);
  const [knownLocations, setKnownLocations] = useState([]);
  const [knownUnits, setKnownUnits] = useState([]);
  const [otherLists, setOtherLists] = useState([]);

  useEffect(() => {
    // Load all lists for switching/discoverability of standalone lists
    fetch("/api/shopping-lists")
      .then((r) => (r.ok ? r.json() : []))
      .then((lists) => setOtherLists(Array.isArray(lists) ? lists : []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    if (propShoppingListId) {
      // Direct load for standalone shopping list or specific id (reuses edit UI)
      fetch(`/api/shopping-lists/${propShoppingListId}`)
        .then((response) => {
          if (!response.ok) throw new Error("Failed to load shopping list");
          return response.json();
        })
        .then((data) => {
          setShoppingList(data);
          setEditedItems(data.items || []);
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message);
          setLoading(false);
        });
      return;
    }
    // Original: Try to fetch existing shopping lists for this meal plan
    fetch("/api/shopping-lists")
      .then((response) => response.json())
      .then((lists) => {
        const existing = lists.find((list) => list.meal_plan_id === mealPlanId);
        if (existing) {
          setShoppingList(existing);
          setEditedItems(existing.items || []);
        }
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [mealPlanId, propShoppingListId]);

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

  const handleCreateNewList = (defaultName = "New Shopping List") => {
    const listName =
      window.prompt("Enter name for new shopping list:", defaultName) ||
      defaultName;
    setLoading(true);
    fetch("/api/shopping-lists", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name: listName }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to create shopping list");
        }
        return response.json();
      })
      .then((data) => {
        setShoppingList(data);
        setEditedItems(data.items || []);
        setLoading(false);
        setEditMode(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  };

  const handleItemChange = (index, field, value) => {
    const updated = [...editedItems];
    updated[index][field] = value;
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
      { name: "", quantity: "", unit: "", location: "", purchased: false },
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
        alert("Shopping list saved successfully!");
      })
      .catch((error) => {
        alert(`Error saving shopping list: ${error.message}`);
      });
  };

  if (loading) {
    return <p className="text-gray-500">Loading shopping list...</p>;
  }

  if (error) {
    return <p className="text-red-500">Error: {error}</p>;
  }

  if (!shoppingList) {
    return (
      <div className="bg-white shadow-md rounded-lg p-6 mt-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          Shopping List
        </h2>
        <p className="text-gray-600 mb-4">
          No shopping list associated with this meal plan yet.
        </p>
        {mealPlanId && (
          <button
            onClick={handleGenerateList}
            className="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded mr-2"
          >
            Generate from Meal Plan
          </button>
        )}
        <button
          onClick={() => handleCreateNewList()}
          className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
        >
          Create New Shopping List
        </button>
        <p className="text-xs text-gray-500 mt-2">
          Creates a standalone empty list (you can add items manually after).
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-md rounded-lg p-6 mt-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-gray-800">
          Shopping List: {shoppingList.name}
        </h2>
        <div className="flex gap-2">
          {!editMode ? (
            <>
              <button
                onClick={() => setEditMode(true)}
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
              >
                Edit
              </button>
              <a
                href={`/shopping-lists/${shoppingList.id}/pdf`}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded inline-block"
              >
                Download PDF
              </a>
            </>
          ) : (
            <>
              <button
                onClick={handleSave}
                className="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded"
              >
                Save
              </button>
              <button
                onClick={() => {
                  setEditedItems(shoppingList.items || []);
                  setEditMode(false);
                }}
                className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded"
              >
                Cancel
              </button>
            </>
          )}
        </div>
      </div>

      {/* Minimal picker for other/standalone lists for discoverability (reuses existing load/edit) */}
      {otherLists.length > 1 && (
        <div className="mb-4 text-sm">
          <span className="text-gray-600 mr-2">Switch to saved list:</span>
          {otherLists
            .filter((l) => l.id !== shoppingList.id)
            .map((l) => (
              <button
                key={l.id}
                onClick={() => {
                  setShoppingList(l);
                  setEditedItems(l.items || []);
                  setEditMode(false);
                }}
                className="mr-2 mb-1 px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded text-xs"
                title={l.meal_plan_id ? `From meal plan` : `Standalone`}
              >
                {l.name}
              </button>
            ))}
          <button
            onClick={() => handleCreateNewList("New List")}
            className="px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded text-xs"
          >
            + New
          </button>
        </div>
      )}

      {editMode ? (
        <div>
          <div className="space-y-2 mb-4">
            {editedItems.map((item, index) => (
              <div key={index} className="flex gap-2 items-center">
                <input
                  type="text"
                  placeholder="Item name"
                  value={item.name}
                  onChange={(e) =>
                    handleItemChange(index, "name", e.target.value)
                  }
                  list="known-ingredients"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  placeholder="Qty"
                  value={item.quantity}
                  onChange={(e) =>
                    handleItemChange(index, "quantity", e.target.value)
                  }
                  className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  placeholder="Unit"
                  value={item.unit}
                  onChange={(e) =>
                    handleItemChange(index, "unit", e.target.value)
                  }
                  list="known-units"
                  className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  placeholder="Location"
                  value={item.location || ""}
                  onChange={(e) =>
                    handleItemChange(index, "location", e.target.value)
                  }
                  list="known-locations"
                  className="w-28 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  title="Location / aisle for grouping"
                />
                <button
                  onClick={() => handleRemoveItem(index)}
                  className="bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
          <button
            onClick={handleAddItem}
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
          >
            Add Item
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
        <ul className="space-y-2">
          {editedItems.map((item, index) => (
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
              >
                {item.quantity && item.unit
                  ? `${item.quantity} ${item.unit} ${item.name}`
                  : item.quantity
                    ? `${item.quantity} ${item.name}`
                    : item.name}
                {item.location ? ` (${item.location})` : ""}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

ShoppingListView.propTypes = {
  mealPlanId: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  mealPlanName: PropTypes.string,
  shoppingListId: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export default ShoppingListView;
