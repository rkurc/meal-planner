"""
Defines the Ingredient data model.
"""

import uuid
from typing import Optional, Union


class Ingredient:  # pylint: disable=too-few-public-methods
    """Represents a single ingredient *as used in a recipe*.

    Legacy master data (from produkty.csv) for an "ingredient":
      - id: unique key
      - nazwa: name
      - idJednostki: unit (references jednostki.csv)
      - idLokalizacji: location id (references lokalizacje.csv)

    In a recipe (skladniki.csv row):
      - quantity = "liczba"
      - name/unit/location_id are denormalized from the linked produkt
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        name: str,
        quantity: Union[float, str],
        unit: str,
        location_id: Optional[str] = None,
        location: Optional[str] = None,
        ingredient_id: Optional[uuid.UUID] = None,
    ):
        """
        Initializes an Ingredient instance.

        Args:
            name: The name of the ingredient (from produkty.nazwa).
            quantity: The amount (from skladniki.liczba).
            unit: The unit of measure (resolved name from jednostki.csv via produkt.idJednostki).
            location_id: The location id (from produkt.idLokalizacji).
            location: The human-readable location name (from lokalizacje.csv), for grouping.
        """
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.location_id = location_id
        self.location = location
        self.ingredient_id = ingredient_id

    def __repr__(self):
        return (
            f"<Ingredient(name='{self.name}', quantity={self.quantity}, "
            f"unit='{self.unit}', location={self.location}, location_id={self.location_id})>"
        )


class MasterIngredient:  # pylint: disable=too-few-public-methods
    """Catalog ingredient (name, default unit, aisle). No quantity."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        name: str,
        default_unit: str = "",
        location: Optional[str] = None,
        location_id: Optional[str] = None,
        ingredient_id: Optional[uuid.UUID] = None,
    ):
        self.ingredient_id = ingredient_id if ingredient_id else uuid.uuid4()
        self.name = name
        self.default_unit = default_unit or ""
        self.location = location
        self.location_id = location_id

    def __repr__(self):
        return (
            f"<MasterIngredient(id={self.ingredient_id}, name='{self.name}', "
            f"default_unit='{self.default_unit}')>"
        )
