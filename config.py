import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'sua_chave_secreta_muito_dificil')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///frecomu.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'

class ReplitConfig(Config):
    """Replit-specific configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    # Use environment variables that Replit provides
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    # Replit uses ephemeral storage, so we'll use SQLite in memory or a persistent volume
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///frecomu.db')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'replit': ReplitConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
