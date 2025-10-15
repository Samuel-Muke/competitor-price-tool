import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="templates", static_folder="static")
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-change-me')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import models
        from . import models
        
        # Create tables
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Database initialization warning: {e}")

        # Register blueprints
        from .auth import auth_bp
        from .properties import properties_bp
        from .dashboard import dashboard_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(properties_bp, url_prefix="/properties")
        app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    return app