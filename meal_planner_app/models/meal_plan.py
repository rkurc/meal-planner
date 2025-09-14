"""
Defines the MealPlan SQLAlchemy model and the association table for the
many-to-many relationship between meal plans and recipes.
"""
import uuid
from ..database import db

# Association table for the many-to-many relationship between MealPlan and Recipe
mealplan_recipes = db.Table('mealplan_recipes',
    db.Column('meal_plan_id', db.String(36), db.ForeignKey('meal_plans.id'), primary_key=True),
    db.Column('recipe_id', db.String(36), db.ForeignKey('recipes.id'), primary_key=True)
)

class MealPlan(db.Model):
    """
    Represents a meal plan, which is a collection of recipes.
    """
    __tablename__ = 'meal_plans'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    recipes = db.relationship('Recipe', secondary=mealplan_recipes, lazy='subquery',
                              backref=db.backref('meal_plans', lazy=True))

    def __repr__(self):
        return f"<MealPlan {self.name}>"
