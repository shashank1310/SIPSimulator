#!/usr/bin/env python3
"""
Configuration file for SIP Simulator
"""

import os
from dotenv import load_dotenv
from datetime import timedelta

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

    # Fund data provider settings
    FUND_DATA_PROVIDER = os.getenv('FUND_DATA_PROVIDER', 'hybrid')  # Options: mfapi, amfi, rapidapi, hybrid
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')  # Optional for RapidAPI provider
    
    # Cache settings
    NAV_CACHE_DURATION = int(os.getenv('NAV_CACHE_DURATION', 1800))  # 30 minutes default
    
    # API settings
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 50))
    
    # Performance settings
    ENABLE_PARALLEL_PROCESSING = os.getenv('ENABLE_PARALLEL_PROCESSING', 'True').lower() == 'true'
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
    
    # Data source priorities (for hybrid provider)
    DATA_SOURCE_PRIORITY = [
        'mfapi',    # Free, good coverage
        'amfi',     # Official, comprehensive but slower
        'rapidapi'  # Paid, fastest but requires key
    ]
    
    # Fallback settings
    ENABLE_MOCK_DATA_FALLBACK = os.getenv('ENABLE_MOCK_DATA_FALLBACK', 'True').lower() == 'true'
    MIN_NAV_RECORDS_REQUIRED = int(os.getenv('MIN_NAV_RECORDS_REQUIRED', 10))
    
    # Logging
    ENABLE_API_LOGGING = os.getenv('ENABLE_API_LOGGING', 'True').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    FUND_DATA_PROVIDER = 'hybrid'
    ENABLE_MOCK_DATA_FALLBACK = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECURITY_HEADERS = True
    LOG_LEVEL = 'WARNING'
    FUND_DATA_PROVIDER = 'hybrid'
    CACHE_DURATION = 7200  # 2 hours in production
    NAV_CACHE_DURATION = 3600  # 1 hour in production

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    FUND_DATA_PROVIDER = 'mfapi'  # Use single provider for consistent testing
    CACHE_DURATION = 60  # Short cache for testing
    ENABLE_MOCK_DATA_FALLBACK = True

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

# Data source configuration
FUND_DATA_SOURCES = {
    'mfapi': {
        'name': 'MF API',
        'description': 'Free Indian Mutual Fund API',
        'website': 'https://www.mfapi.in/',
        'requires_key': False,
        'coverage': 'High',
        'speed': 'Medium',
        'reliability': 'High'
    },
    'amfi': {
        'name': 'AMFI',
        'description': 'Association of Mutual Funds in India',
        'website': 'https://www.amfiindia.com/',
        'requires_key': False,
        'coverage': 'Complete',
        'speed': 'Slow',
        'reliability': 'Very High'
    },
    'rapidapi': {
        'name': 'RapidAPI',
        'description': 'Premium mutual fund data service',
        'website': 'https://rapidapi.com/',
        'requires_key': True,
        'coverage': 'High',
        'speed': 'Fast',
        'reliability': 'High'
    },
    'hybrid': {
        'name': 'Hybrid',
        'description': 'Combines multiple sources for best coverage',
        'website': 'N/A',
        'requires_key': False,
        'coverage': 'Complete',
        'speed': 'Fast',
        'reliability': 'Very High'
    }
}

# Environment-specific settings
def load_environment_config():
    """Load configuration from environment variables or .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv not installed, use environment variables directly

# Load environment config on import
load_environment_config() 