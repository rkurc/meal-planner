import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class ShoppingListItem:
    """Represents a single item in a shopping list."""

    name: str
    quantity: Union[str, float, List[Union[str, float]]]
    unit: str
    purchased: bool = False
    location: Optional[str] = None
    location_id: Optional[str] = None


@dataclass
class ShoppingList:
    """Represents a shopping list, typically generated from a meal plan."""

    name: str
    items: List[ShoppingListItem] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    meal_plan_id: uuid.UUID = field(default_factory=uuid.uuid4)
