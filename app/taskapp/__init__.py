import os
import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

db = SQLAlchemy()


def init_database(app, retries=30, delay=2):
    """Create the tables, waiting for the database to accept connections."""
    for attempt in range(1, retries + 1):
        try:
            with app.app_context():
                db.create_all()
            return
        except OperationalError:
            app.logger.warning("Database not ready (attempt %s/%s)", attempt, retries)
            if attempt == retries:
                raise
            time.sleep(delay)


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///tasks.db"
    )
    app.config["APP_VERSION"] = os.environ.get("APP_VERSION", "dev")
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from . import routes

    app.register_blueprint(routes.bp)

    if app.config.get("TESTING"):
        with app.app_context():
            db.create_all()
    else:
        init_database(app)
    return app
