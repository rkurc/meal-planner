"""Draft recipe shape returned by parse. Matches POST /api/recipes fields."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ParsedIngredient:
    """One ingredient line on a parsed draft (not persisted)."""

    name: str
    quantity: str = ""
    unit: str = ""
    location: str = ""

    def to_dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "location": self.location,
        }


@dataclass
class ParsedRecipe:
    """Structured draft. is_usable matches create-recipe required fields."""

    name: str = ""
    description: str = ""
    instructions: str = ""
    source_url: str = ""
    ingredients: List[ParsedIngredient] = field(default_factory=list)
    parser: str = "llm"
    model: str = ""

    def is_usable(self) -> bool:
        return bool((self.name or "").strip() and (self.instructions or "").strip())

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description or "",
            "instructions": self.instructions,
            "source_url": self.source_url or "",
            "ingredients": [item.to_dict() for item in self.ingredients],
            "meta": {"parser": self.parser, "model": self.model},
        }
