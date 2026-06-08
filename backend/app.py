from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler
import os

from config.settings import Config
from config.database import DatabaseConfig
from middleware.error import register_error_handlers
from controllers.auth import auth
from controllers.repo import repo
from controllers.metrics import metrics
from models.user import UserModel

def create_app():
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(Config)

    # Create necessary directories
    Config.create_directories()

    # Configure logging
    handler = RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=10000000,  # 10MB
        backupCount=5
    )
    handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
    app.logger.addHandler(handler)
    app.logger.setLevel(Config.LOG_LEVEL)

    # Initialize extensions
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:3000"],  # Explicitly allow React dev server
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "expose_headers": ["Content-Type", "Authorization"]
         }}
    )
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[Config.RATELIMIT_DEFAULT]
    )

    # Register error handlers
    register_error_handlers(app)

    # Initialize database
    try:
        # Create database if it doesn't exist
        DatabaseConfig.create_database()
        
        # Initialize connection pool
        app.db_pool = DatabaseConfig.get_connection_pool()
        
        # Initialize user model to create tables
        UserModel()
        
        app.logger.info("Database and tables initialized successfully")
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {str(e)}")
        raise

    # Register blueprints
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(repo, url_prefix='/repo')
    app.register_blueprint(metrics, url_prefix='/metrics')

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)

