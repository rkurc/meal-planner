"""
Defines the Ingredient data model.
"""

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

    def __repr__(self):
        return (
            f"<Ingredient(name='{self.name}', quantity={self.quantity}, "
            f"unit='{self.unit}', location={self.location}, location_id={self.location_id})>"
        )
