import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'https://jwt.io/#debugger-io?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c')
    DEBUG = os.environ.get('FLASK_DEBUG', True)
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'code-doctore-secret-key-2024')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # GitHub API settings
    GITHUB_API_URL = "https://api.github.com"
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', 'xxxxx)
    
    # File paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    REPOS_DIR = os.path.join(BASE_DIR, 'repos')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Create necessary directories
    @staticmethod
    def create_directories():
        os.makedirs(Config.REPOS_DIR, exist_ok=True)
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
    
    # CORS settings
    CORS_ORIGINS = [
        "http://localhost:3000",  # React development server
        "http://localhost:5000",  # Flask development server
    ]
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = os.path.join(LOGS_DIR, "app.log") 