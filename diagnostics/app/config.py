import os
from datetime import timedelta

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # MongoDB configuration
    MONGO_URI = os.environ.get('MONGO_URI')
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'json', 'pkl'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Model configuration
    MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    
    # Dataset configuration
    DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets')
    
    # WebSocket configuration
    WS_PORT = int(os.environ.get('WS_PORT', 8765))
    
    # API configuration
    API_VERSION = '1.0'
    CORS_HEADERS = ['Content-Type', 'Authorization']
    
    # Cache configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300