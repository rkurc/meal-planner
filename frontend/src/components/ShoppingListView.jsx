import React, { useState, useEffect } from "react";

const ShoppingListView = ({ mealPlanId, mealPlanName }) => {
    const [shoppingList, setShoppingList] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editMode, setEditMode] = useState(false);
    const [editedItems, setEditedItems] = useState([]);

    useEffect(() => {
        // Try to fetch existing shopping lists for this meal plan
        fetch("/api/shopping-lists")
            .then((response) => response.json())
            .then((lists) => {
                const existing = lists.find(
                    (list) => list.meal_plan_id === mealPlanId,
                );
                if (existing) {
                    setShoppingList(existing);
                    setEditedItems(existing.items || []);
                }
                setLoading(false);
            })
            .catch((error) => {
                setError(error.message);
                setLoading(false);
            });
    }, [mealPlanId]);

    const handleGenerateList = () => {
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
            { name: "", quantity: "", unit: "", purchased: false },
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
                    No shopping list has been generated yet for this meal plan.
                </p>
                <button
                    onClick={handleGenerateList}
                    className="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded"
                >
                    Generate Shopping List
                </button>
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
                                href={`/meal-plans/${mealPlanId}/shopping-list/pdf`}
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
                                    className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                            </span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default ShoppingListView;
