"""
Defines the MealPlan data model.
"""

import uuid
from typing import List, Optional, Dict, Any


class MealPlan:  # pylint: disable=too-few-public-methods,too-many-arguments,too-many-positional-arguments
    """Represents a meal plan, which is a collection of recipes for a period (e.g., a week)."""

    def __init__(
        self,
        name: str,
        description: str = "",
        recipe_ids: Optional[List[uuid.UUID]] = None,
        recipes: Optional[List[Dict[str, Any]]] = None,
        meal_plan_id: Optional[uuid.UUID] = None,
    ):
        """
        Initializes a MealPlan instance.

        Args:
            name: The name of the meal plan (e.g., "Week 1 Dinners").
            description: A short description of the meal plan.
            recipe_ids: Legacy list of recipe UUIDs (converted to recipes w/ count=1).
            recipes: New list of dicts e.g. [{"id": uuid, "count": 1.5}].
            meal_plan_id: An optional UUID for the meal plan; one is generated if not provided.
        """
        self.meal_plan_id = meal_plan_id if meal_plan_id else uuid.uuid4()
        self.name = name
        self.description = description
        if recipes is not None:
            self._recipe_entries = self._normalize_recipes(recipes)
        elif recipe_ids is not None:
            self._recipe_entries = self._normalize_recipes(
                [{"recipe_id": rid, "count": 1.0} for rid in recipe_ids]
            )
        else:
            self._recipe_entries = []

    def _normalize_recipes(  # pylint: disable=line-too-long
        self, entries: Optional[list] = None
    ) -> List[Dict[str, Any]]:
        """Normalize input (legacy/new) to list of {recipe_id:UUID, count:float}.
        Merges dups by sum; supports fractions.
        """
        if not entries:
            return []
        by_id: Dict[uuid.UUID, float] = {}
        for entry in entries:
            rid = None
            cnt: float = 1.0
            if isinstance(entry, dict):
                rid = entry.get("recipe_id") or entry.get("id")
                raw_cnt = entry.get("count", entry.get("quantity", 1.0))
                try:
                    cnt = float(raw_cnt)
                except (ValueError, TypeError):
                    cnt = 1.0
            elif isinstance(entry, (uuid.UUID, str)):
                rid = entry
                cnt = 1.0
            if rid is None:
                continue
            try:
                rid_uuid = (
                    uuid.UUID(str(rid)) if not isinstance(rid, uuid.UUID) else rid
                )
            except (ValueError, AttributeError, TypeError):
                continue
            if rid_uuid in by_id:
                by_id[rid_uuid] += cnt
            else:
                by_id[rid_uuid] = cnt
        return [{"recipe_id": rid, "count": cnt} for rid, cnt in by_id.items()]

    @property
    def recipes(self) -> List[Dict[str, Any]]:
        """Primary: recipe entries w/ counts. Live list (mutations for add/remove compat)."""
        return self._recipe_entries

    @recipes.setter
    def recipes(self, value: Optional[List[Dict[str, Any]]]) -> None:
        self._recipe_entries = self._normalize_recipes(value)

    @property
    def recipe_ids(self) -> List[uuid.UUID]:
        """Legacy compatibility property returning just the ids (counts ignored for this view).
        Supports reading and assignment from old code/templates/crud.
        """
        return [e["recipe_id"] for e in self._recipe_entries]

    @recipe_ids.setter
    def recipe_ids(self, value: Optional[List[uuid.UUID]]) -> None:
        self._recipe_entries = self._normalize_recipes(
            [{"recipe_id": rid, "count": 1.0} for rid in (value or [])]
        )

    def __repr__(self):
        return (
            f"<MealPlan(id={self.meal_plan_id}, name='{self.name}', "
            f"recipes_count={len(self._recipe_entries)})>"
        )
