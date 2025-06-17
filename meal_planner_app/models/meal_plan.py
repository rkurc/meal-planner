import uuid
from typing import List, Optional

class MealPlan:
    """Represents a meal plan, which is a collection of recipes for a period (e.g., a week)."""
    def __init__(self,
                 name: str,
                 recipe_ids: Optional[List[uuid.UUID]] = None,
                 id: Optional[uuid.UUID] = None):
        """
        Initializes a MealPlan instance.

        Args:
            name: The name of the meal plan (e.g., "Week 1 Dinners").
            recipe_ids: A list of recipe UUIDs included in this plan. Defaults to an empty list.
            id: An optional UUID for the meal plan; one is generated if not provided.
        """
        self.id = id if id else uuid.uuid4()
        self.name = name
        self.recipe_ids = recipe_ids if recipe_ids is not None else []

    def __repr__(self):
        return f"<MealPlan(id={self.id}, name='{self.name}', recipe_ids_count={len(self.recipe_ids)})>"
