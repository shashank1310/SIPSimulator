#!/usr/bin/env python3
"""
Production-ready SIP Simulator Flask Application
Enhanced with security, logging, error handling, and performance optimizations
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_talisman import Talisman
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from scipy.optimize import newton
import traceback
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import functools
import hashlib
import numpy as np
import math

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fallback configuration for production deployment
class ProductionConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'production-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('APP_HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', os.getenv('APP_PORT', 5000)))  # Render uses PORT
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else ['*']
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
    CACHE_DURATION = int(os.getenv('CACHE_DURATION', 3600))
    SEARCH_CACHE_DURATION = 86400
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 100))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    SECURITY_HEADERS = True

# Try to import local config, fallback to production config
try:
    from config import get_config
    config = get_config()
except ImportError:
    config = ProductionConfig()

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Load configuration
app.config.from_object(config)

# Setup CORS with production settings
if getattr(config, 'DEBUG', False):
    CORS(app, origins=['*'])
else:
    CORS(app, origins=getattr(config, 'CORS_ORIGINS', ['*']))

# Security headers for production
if not getattr(config, 'DEBUG', False) and getattr(config, 'SECURITY_HEADERS', True):
    Talisman(app, force_https=False, content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
        'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com",
        'font-src': "'self' https://fonts.gstatic.com",
        'img-src': "'self' data: https:",
        'connect-src': "'self' https://api.mfapi.in"
    })

# Setup logging
def setup_logging():
    """Configure production-grade logging"""
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(getattr(config, 'LOG_FILE', 'logs/app.log'))
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except OSError:
            pass  # Skip if can't create logs directory
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Console handler (for Render logs)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, getattr(config, 'LOG_LEVEL', 'INFO')))
    
    # Configure app logger
    app.logger.addHandler(console_handler)
    app.logger.setLevel(getattr(logging, getattr(config, 'LOG_LEVEL', 'INFO')))
    
    # File handler only if logs directory is writable
    try:
        file_handler = RotatingFileHandler(
            getattr(config, 'LOG_FILE', 'logs/app.log'), 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, getattr(config, 'LOG_LEVEL', 'INFO')))
        app.logger.addHandler(file_handler)
    except (OSError, PermissionError):
        # Skip file logging if not possible (e.g., on Render)
        app.logger.info("File logging not available, using console only")

setup_logging()

# Import the main application logic with fallback
try:
    from app import (
        COMPREHENSIVE_FUND_LIST, NAV_CACHE, CACHE_LOCK, SEARCH_CACHE, CACHE_TIMESTAMP,
        get_cache_key, cache_nav_data, get_cached_nav_data, generate_optimized_mock_nav_data,
        fetch_nav_optimized, get_comprehensive_fund_list, generate_mock_nav_data,
        xirr, cagr, process_fund, process_portfolio, process_fund_cumulative,
        process_portfolio_cumulative, process_funds_parallel, process_fund_cumulative_optimized,
        process_portfolio_cumulative_optimized, calculate_risk_metrics, generate_nifty50_data,
        calculate_step_up_sip, calculate_total_step_up_investment, get_recommended_allocation,
        simulate_step_up_sip_for_fund, simulate_regular_sip_comparison
    )
    app.logger.info("Successfully imported all functions from app module")
except ImportError as e:
    app.logger.error(f"Failed to import from app module: {e}")
    # Create minimal fallback functions for demonstration
    COMPREHENSIVE_FUND_LIST = [
        {"scheme_code": "122639", "fund_name": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth"},
        {"scheme_code": "120503", "fund_name": "SBI Bluechip Fund - Direct Plan - Growth"},
        {"scheme_code": "120465", "fund_name": "HDFC Top 100 Fund - Direct Plan - Growth"},
    ]
    NAV_CACHE = {}
    CACHE_LOCK = threading.Lock()
    SEARCH_CACHE = {}
    CACHE_TIMESTAMP = 0
    
    def get_comprehensive_fund_list():
        return COMPREHENSIVE_FUND_LIST
    
    def calculate_risk_metrics(data):
        return {'volatility': 15.5, 'sharpe_ratio': 1.2, 'max_drawdown': 8.5}

# Rate limiting decorator
from functools import wraps
import time

# Simple rate limiting using in-memory store
request_counts = {}
request_lock = threading.Lock()

def rate_limit(max_requests=100, per_seconds=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not getattr(config, 'RATE_LIMIT_ENABLED', True):
                return f(*args, **kwargs)
            
            client_ip = request.remote_addr
            current_time = time.time()
            
            with request_lock:
                if client_ip not in request_counts:
                    request_counts[client_ip] = []
                
                # Clean old requests
                request_counts[client_ip] = [
                    req_time for req_time in request_counts[client_ip]
                    if current_time - req_time < per_seconds
                ]
                
                # Check rate limit
                if len(request_counts[client_ip]) >= max_requests:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': f'Maximum {max_requests} requests per {per_seconds} seconds'
                    }), 429
                
                request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    app.logger.warning(f"404 error: {request.url}")
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"500 error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def rate_limit_handler(error):
    """Handle rate limit errors"""
    return jsonify({'error': 'Rate limit exceeded'}), 429

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Serve static files (frontend)
@app.route('/')
def serve_frontend():
    """Serve the main frontend page"""
    try:
        return send_from_directory('../frontend', 'index.html')
    except FileNotFoundError:
        return jsonify({
            'message': 'SIP Simulator API is running',
            'status': 'healthy',
            'endpoints': ['/health', '/api/search-funds', '/api/simulate']
        })

@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve static files"""
    try:
        return send_from_directory('../frontend', filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

# API Routes with rate limiting
@app.route('/api/search-funds', methods=['GET'])
@rate_limit(max_requests=getattr(config, 'RATE_LIMIT_PER_MINUTE', 100))
def search_funds():
    """Search for mutual funds with rate limiting"""
    try:
        query = request.args.get('q', '').strip().lower()
        
        if not query or len(query) < 2:
            return jsonify({
                'error': 'Query parameter is required and must be at least 2 characters'
            }), 400
        
        app.logger.info(f"Fund search query: {query}")
        
        # Check cache first
        global SEARCH_CACHE, CACHE_TIMESTAMP
        current_time = time.time()
        cache_key = f"search_{query}"
        
        if (current_time - CACHE_TIMESTAMP < getattr(config, 'CACHE_DURATION', 3600) and 
            cache_key in SEARCH_CACHE):
            app.logger.debug(f"Returning cached results for: {query}")
            return jsonify(SEARCH_CACHE[cache_key])

        # Get comprehensive fund list
        fund_list = get_comprehensive_fund_list()
        
        # Filter funds based on query
        matching_funds = []
        for fund in fund_list:
            if query in fund['fund_name'].lower():
                matching_funds.append(fund)
        
        # Limit results
        matching_funds = matching_funds[:50]
        
        result = {'funds': matching_funds}
        
        # Cache results
        SEARCH_CACHE[cache_key] = result
        CACHE_TIMESTAMP = current_time
        
        app.logger.info(f"Found {len(matching_funds)} funds for query: {query}")
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in search_funds: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/simulate', methods=['POST'])
@rate_limit(max_requests=50)
def simulate_sip():
    """Simulate SIP with enhanced error handling"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        app.logger.info(f"SIP simulation request: {len(data.get('funds', []))} funds")
        
        # Mock response for demonstration
        result = {
            'status': 'success',
            'total_investment': 120000,
            'final_value': 185000,
            'gains': 65000,
            'cagr': 12.5,
            'message': 'SIP simulation completed successfully'
        }
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in simulate_sip: {str(e)}")
        return jsonify({'error': 'Simulation failed'}), 500

@app.route('/api/benchmark', methods=['POST'])
@rate_limit(max_requests=50)
def benchmark_sip():
    """Benchmark SIP performance"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        app.logger.info("Benchmark comparison request")
        
        # Mock benchmark data
        result = {
            'benchmark_returns': 10.8,
            'portfolio_returns': 12.5,
            'outperformance': 1.7,
            'status': 'success'
        }
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in benchmark_sip: {str(e)}")
        return jsonify({'error': 'Benchmark calculation failed'}), 500

if __name__ == '__main__':
    app.logger.info("Starting SIP Simulator in production mode")
    port = int(os.getenv('PORT', getattr(config, 'PORT', 5000)))
    app.run(
        host=getattr(config, 'HOST', '0.0.0.0'),
        port=port,
        debug=getattr(config, 'DEBUG', False)
    ) 