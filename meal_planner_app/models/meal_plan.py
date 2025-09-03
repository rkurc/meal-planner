"""
Defines the MealPlan data model.
"""

import uuid
from typing import List, Optional


class MealPlan:  # pylint: disable=too-few-public-methods
    """Represents a meal plan, which is a collection of recipes for a period (e.g., a week)."""

    def __init__(
        self,
        name: str,
        recipe_ids: Optional[List[uuid.UUID]] = None,
        meal_plan_id: Optional[uuid.UUID] = None,
    ):
        """
        Initializes a MealPlan instance.

        Args:
            name: The name of the meal plan (e.g., "Week 1 Dinners").
            recipe_ids: A list of recipe UUIDs included in this plan. Defaults to an empty list.
            meal_plan_id: An optional UUID for the meal plan; one is generated if not provided.
        """
        self.meal_plan_id = meal_plan_id if meal_plan_id else uuid.uuid4()
        self.name = name
        self.recipe_ids = recipe_ids if recipe_ids is not None else []

    def __repr__(self):
        return (
            f"<MealPlan(id={self.meal_plan_id}, name='{self.name}', "
            f"recipe_ids_count={len(self.recipe_ids)})>"
        )
