"""
Defines the Recipe SQLAlchemy model.
"""

import uuid
from ..database import db


class Recipe(db.Model):
    """
    Represents a recipe with ingredients, instructions, and other details.
    """

    __tablename__ = "recipes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(255), nullable=True)

    ingredients = db.relationship(
        "Ingredient", backref="recipe", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Recipe {self.name}>"
