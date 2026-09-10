import React from "react";
import PropTypes from "prop-types";

const IngredientLineFields = ({
  item,
  onChange,
  onRemove,
  namePlaceholder,
  quantityPlaceholder,
  unitPlaceholder,
  locationPlaceholder,
  locationTitle,
  removeLabel,
  removeDisabled,
  listIds,
}) => {
  return (
    <div className="flex gap-2 mb-2">
      <input
        type="text"
        placeholder={namePlaceholder}
        value={item.name}
        onChange={(e) => onChange("name", e.target.value)}
        list={listIds.ingredients}
        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <input
        type="text"
        placeholder={quantityPlaceholder}
        value={item.quantity}
        onChange={(e) => onChange("quantity", e.target.value)}
        className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <input
        type="text"
        placeholder={unitPlaceholder}
        value={item.unit}
        onChange={(e) => onChange("unit", e.target.value)}
        list={listIds.units}
        className="w-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <input
        type="text"
        placeholder={locationPlaceholder}
        value={item.location || ""}
        onChange={(e) => onChange("location", e.target.value)}
        list={listIds.locations}
        className="w-28 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        title={locationTitle}
      />
      <button
        type="button"
        onClick={onRemove}
        className="bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded-md"
        disabled={removeDisabled}
      >
        {removeLabel}
      </button>
    </div>
  );
};

IngredientLineFields.propTypes = {
  item: PropTypes.shape({
    name: PropTypes.string,
    quantity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    unit: PropTypes.string,
    location: PropTypes.string,
  }).isRequired,
  onChange: PropTypes.func.isRequired,
  onRemove: PropTypes.func.isRequired,
  namePlaceholder: PropTypes.string,
  quantityPlaceholder: PropTypes.string,
  unitPlaceholder: PropTypes.string,
  locationPlaceholder: PropTypes.string,
  locationTitle: PropTypes.string,
  removeLabel: PropTypes.string,
  removeDisabled: PropTypes.bool,
  listIds: PropTypes.shape({
    ingredients: PropTypes.string,
    units: PropTypes.string,
    locations: PropTypes.string,
  }).isRequired,
};

export default IngredientLineFields;
