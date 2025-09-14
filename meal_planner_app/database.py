"""
Initializes the SQLAlchemy database object.
This is kept in a separate file to prevent circular imports.
"""
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance
db = SQLAlchemy()
