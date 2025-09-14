"""
Application factory for the Meal Planner App.
"""

import os
from flask import Flask
from .database import db


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # --- Configuration ---
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'meal_planner.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # --- Ensure instance folder exists ---
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # --- Initialize Extensions ---
    db.init_app(app)

    # --- Register Blueprints ---
    # pylint: disable=import-outside-toplevel
    from . import main

    app.register_blueprint(main.bp)

    return app
