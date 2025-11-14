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
    
    # Enhanced Configuration for MySQL
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-change-me-nairobi-2024')
    
    # MySQL Configuration for Nairobi deployment
    mysql_host = os.getenv('MYSQL_HOST', 'localhost')
    mysql_user = os.getenv('MYSQL_USER', 'root')
    mysql_password = os.getenv('MYSQL_PASSWORD', '')
    mysql_db = os.getenv('MYSQL_DB', 'Aggregator')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI', 
        f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}?charset=utf8mb4'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }

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
        from .main import main_bp  # New landing page blueprint
        
        app.register_blueprint(main_bp)  # Landing page routes
        app.register_blueprint(auth_bp)
        app.register_blueprint(properties_bp, url_prefix="/properties")
        app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    return app