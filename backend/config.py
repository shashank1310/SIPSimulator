# Configuration settings for SIP Simulator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('APP_HOST', '0.0.0.0')
    PORT = int(os.getenv('APP_PORT', 5000))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else ['*']
    
    # API Configuration
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
    CACHE_DURATION = int(os.getenv('CACHE_DURATION', 3600))  # 1 hour in seconds
    SEARCH_CACHE_DURATION = 86400  # 24 hours in seconds
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 100))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Security Configuration
    SECURITY_HEADERS = True
    
    # Risk Analysis Configuration
    RISK_FREE_RATE = 0.06  # 6% risk-free rate
    DEFAULT_EXPECTED_RETURN = 0.12  # 12% default expected return
    DEFAULT_INFLATION_RATE = 0.06  # 6% default inflation rate

    # SIP Configuration
    DEFAULT_SIP_AMOUNT = 10000
    MIN_SIP_AMOUNT = 500
    SIP_STEP = 500

    # Chart Configuration
    MAX_CHART_POINTS = 200
    DEFAULT_CHART_MONTHS = 12

    # Fund Categories
    FUND_CATEGORIES = {
        'LARGE_CAP': 'Large Cap',
        'MID_CAP': 'Mid Cap', 
        'SMALL_CAP': 'Small Cap',
        'MULTI_CAP': 'Multi Cap',
        'DEBT': 'Debt',
        'HYBRID': 'Hybrid',
        'EQUITY': 'Equity'
    }

    # Risk Levels
    RISK_LEVELS = {
        'LOW': 'Low',
        'MEDIUM': 'Medium', 
        'HIGH': 'High'
    }

    # Asset Allocation Templates
    ASSET_ALLOCATION_TEMPLATES = {
        'AGGRESSIVE': {'equity': 80, 'debt': 15, 'gold': 5},
        'MODERATE': {'equity': 70, 'debt': 25, 'gold': 5},
        'CONSERVATIVE': {'equity': 60, 'debt': 35, 'gold': 5},
        'CAPITAL_PRESERVATION': {'equity': 40, 'debt': 55, 'gold': 5}
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECURITY_HEADERS = True
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default']) 