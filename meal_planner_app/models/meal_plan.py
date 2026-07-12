"""
Defines the MealPlan data model.
"""

import uuid
from typing import List, Optional, Dict, Any


def _normalize_recipe_entries(entries):
    """Normalize to [{'recipe_id': UUID, 'count': float}, ...].
    Accepts legacy list[uuid] or new list[dict with id/count]. Merges dups by sum.
    """
    if not entries:
        return []
    by_id: Dict[uuid.UUID, float] = {}
    for entry in entries:
        rid = None
        cnt = 1.0
        if isinstance(entry, dict):
            rid = entry.get("recipe_id") or entry.get("id")
            raw = entry.get("count", entry.get("quantity", 1.0))
            try:
                cnt = float(raw)
            except (ValueError, TypeError):
                cnt = 1.0
        elif isinstance(entry, (uuid.UUID, str)):
            rid = entry
        if rid is None:
            continue
        try:
            rid_uuid = uuid.UUID(str(rid)) if not isinstance(rid, uuid.UUID) else rid
        except (ValueError, TypeError):
            continue
        by_id[rid_uuid] = by_id.get(rid_uuid, 0.0) + cnt
    return [{"recipe_id": rid, "count": cnt} for rid, cnt in by_id.items()]


class MealPlan:
    """Represents a meal plan (collection of recipes with optional counts/multipliers)."""

    def __init__(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        name: str,
        description: str = "",
        recipe_ids: Optional[List[uuid.UUID]] = None,
        recipes: Optional[List[Dict[str, Any]]] = None,
        meal_plan_id: Optional[uuid.UUID] = None,
    ):
        self.meal_plan_id = meal_plan_id or uuid.uuid4()
        self.name = name
        self.description = description
        if recipes is not None:
            self._recipes = _normalize_recipe_entries(recipes)
        elif recipe_ids is not None:
            self._recipes = _normalize_recipe_entries(
                [{"recipe_id": rid, "count": 1.0} for rid in recipe_ids]
            )
        else:
            self._recipes = []

    @property
    def recipes(self) -> List[Dict[str, Any]]:
        """Primary representation: list of {recipe_id, count}."""
        return self._recipes

    @recipes.setter
    def recipes(self, value):
        self._recipes = _normalize_recipe_entries(value)

    @property
    def recipe_ids(self) -> List[uuid.UUID]:
        """Legacy view (for old code/templates). Read/write for compat."""
        return [e["recipe_id"] for e in self._recipes]

    @recipe_ids.setter
    def recipe_ids(self, value):
        self._recipes = _normalize_recipe_entries(
            [{"recipe_id": rid, "count": 1.0} for rid in (value or [])]
        )

    def __repr__(self):
        return (
            f"<MealPlan(id={self.meal_plan_id}, name='{self.name}', "
            f"recipes_count={len(self._recipes)})>"
        )
