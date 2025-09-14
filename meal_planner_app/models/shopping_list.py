"""
Defines the ShoppingList and ShoppingListItem SQLAlchemy models.
"""
import uuid
from ..database import db

class ShoppingList(db.Model):
    """
    Represents a shopping list, which is generated from a meal plan.
    """
    __tablename__ = 'shopping_lists'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)

    items = db.relationship('ShoppingListItem', backref='shopping_list', lazy=True, cascade="all, delete-orphan")

    meal_plan_id = db.Column(db.String(36), db.ForeignKey('meal_plans.id'), nullable=True)

    def __repr__(self):
        return f"<ShoppingList {self.name}>"

class ShoppingListItem(db.Model):
    """
    Represents an item on a shopping list.
    """
    __tablename__ = 'shopping_list_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.String(50), nullable=True)
    unit = db.Column(db.String(50), nullable=True)
    purchased = db.Column(db.Boolean, default=False, nullable=False)

    shopping_list_id = db.Column(db.String(36), db.ForeignKey('shopping_lists.id'), nullable=False)

    def __repr__(self):
        return f"<ShoppingListItem {self.name}>"
