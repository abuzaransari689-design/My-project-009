"""
Cloud Based Smart Expressway Traveler System
Main application entry point
"""

from flask import Flask
from models.database import init_db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.emergency import emergency_bp
from routes.admin import admin_bp
import os

def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)

    # Secret key for session management (use env var in production)
    app.secret_key = os.environ.get("SECRET_KEY", "expressway-secret-key-2024")

    # Register blueprints (modular route groups)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(admin_bp)

    # Initialize the SQLite database (creates tables if they don't exist)
    with app.app_context():
        init_db()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
