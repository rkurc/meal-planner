import uuid
from typing import List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .ingredient import Ingredient

class Recipe:
    """Represents a culinary recipe."""
    def __init__(self,
                 name: str,
                 instructions: str,
                 ingredients: Optional[List['Ingredient']] = None,
                 description: Optional[str] = None,
                 source_url: Optional[str] = None,
                 id: Optional[uuid.UUID] = None):
        """
        Initializes a Recipe instance.

        Args:
            name: The name of the recipe.
            instructions: The steps to prepare the recipe.
            ingredients: A list of Ingredient objects for the recipe. Defaults to an empty list.
            description: An optional short description of the recipe.
            source_url: An optional URL to the original source of the recipe.
            id: An optional UUID for the recipe; one is generated if not provided.
        """
        self.id = id if id else uuid.uuid4()
        self.name = name
        self.description = description
        self.ingredients = ingredients if ingredients is not None else []
        self.instructions = instructions
        self.source_url = source_url

    def __repr__(self):
        return f"<Recipe(id={self.id}, name='{self.name}')>"
