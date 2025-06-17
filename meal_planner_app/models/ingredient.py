from typing import Union

class Ingredient:
    """Represents a single ingredient with its quantity and unit."""
    def __init__(self,
                 name: str,
                 quantity: Union[float, str],
                 unit: str):
        """
        Initializes an Ingredient instance.

        Args:
            name: The name of the ingredient (e.g., "Flour", "Sugar").
            quantity: The amount of the ingredient (e.g., 1, 0.5, "to taste").
            unit: The unit of measure (e.g., "cup", "g", "tsp").
        """
        self.name = name
        self.quantity = quantity
        self.unit = unit

    def __repr__(self):
        return f"<Ingredient(name='{self.name}', quantity={self.quantity}, unit='{self.unit}')>"
