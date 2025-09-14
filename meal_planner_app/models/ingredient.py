"""
Defines the Ingredient SQLAlchemy model.
"""
from ..database import db

class Ingredient(db.Model):
    """
    Represents a single ingredient for a recipe in the database.
    """
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.String(50), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    recipe_id = db.Column(db.String(36), db.ForeignKey('recipes.id'), nullable=False)

    def __repr__(self):
        return f"<Ingredient {self.name}>"
