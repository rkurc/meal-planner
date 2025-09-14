"""
Initializes the database by creating all the tables.
"""

from . import create_app, db

# Import models to ensure they are registered with SQLAlchemy
from . import models  # noqa: F401

app = create_app()
with app.app_context():
    db.create_all()

print("Database tables created.")
