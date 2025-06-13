#!/usr/bin/env python3
"""
SIP Simulator - Single Deployment
Serves frontend and uses backend logic directly
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configuration
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'production-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true' and os.getenv('FLASK_ENV') != 'production'
    HOST = os.getenv('APP_HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Initialize Flask app
app = Flask(__name__, static_folder='frontend', static_url_path='')
app.config.from_object(Config)

# Setup CORS
CORS(app, origins=['*'])

# Setup logging
logging.basicConfig(level=getattr(logging, app.config['LOG_LEVEL']))
app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))

# Import backend functionality
try:
    from backend.app import (
        search_funds as backend_search_funds,
        simulate_sip as backend_simulate_sip,
        benchmark_sip as backend_benchmark_sip,
        get_fund_info as backend_get_fund_info,
        get_cumulative_performance as backend_cumulative_performance,
        risk_analysis as backend_risk_analysis,
        goal_planning as backend_goal_planning,
        step_up_sip as backend_step_up_sip
    )
    app.logger.info("Successfully imported backend functions")
except ImportError as e:
    app.logger.error(f"Failed to import backend functions: {e}")
    # Create fallback functions
    def backend_search_funds():
        return jsonify({'error': 'Backend not available'}), 503
    def backend_simulate_sip():
        return jsonify({'error': 'Backend not available'}), 503
    def backend_benchmark_sip():
        return jsonify({'error': 'Backend not available'}), 503
    def backend_get_fund_info(scheme_code):
        return jsonify({'error': 'Backend not available'}), 503
    def backend_cumulative_performance():
        return jsonify({'error': 'Backend not available'}), 503
    def backend_risk_analysis():
        return jsonify({'error': 'Backend not available'}), 503
    def backend_goal_planning():
        return jsonify({'error': 'Backend not available'}), 503
    def backend_step_up_sip():
        return jsonify({'error': 'Backend not available'}), 503

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'message': 'SIP Simulator is running'
    })

# Root endpoint - serve frontend
@app.route('/')
def home():
    """Serve the main frontend page"""
    try:
        return send_from_directory('frontend', 'index.html')
    except FileNotFoundError:
        return jsonify({
            'message': 'SIP Simulator API',
            'status': 'healthy',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'frontend': '/',
                'api': '/api/*'
            }
        })

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        return send_from_directory('frontend', filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

# API Routes - Use backend functions directly
@app.route('/api/search-funds', methods=['GET'])
def search_funds():
    """Search for mutual funds"""
    return backend_search_funds()

@app.route('/api/simulate', methods=['POST'])
def simulate_sip():
    """Simulate SIP investment"""
    return backend_simulate_sip()

@app.route('/api/benchmark', methods=['POST'])
def benchmark_sip():
    """Compare with benchmark"""
    return backend_benchmark_sip()

@app.route('/api/fund-info/<scheme_code>', methods=['GET'])
def get_fund_info(scheme_code):
    """Get fund information"""
    return backend_get_fund_info(scheme_code)

@app.route('/api/cumulative-performance', methods=['POST'])
def cumulative_performance():
    """Get cumulative performance data"""
    return backend_cumulative_performance()

@app.route('/api/risk-analysis', methods=['POST'])
def risk_analysis():
    """Perform risk analysis"""
    return backend_risk_analysis()

@app.route('/api/goal-planning', methods=['POST'])
def goal_planning():
    """Goal-based investment planning"""
    return backend_goal_planning()

@app.route('/api/step-up-sip', methods=['POST'])
def step_up_sip():
    """Step-up SIP calculation"""
    return backend_step_up_sip()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    app.logger.warning(f"404 error: {request.url}")
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = app.config['DEBUG']
    
    if debug_mode:
        app.logger.info("Starting SIP Simulator in development mode")
    else:
        app.logger.info("Starting SIP Simulator in production mode")
    
    app.logger.info(f"Server will run on port {port}")
    app.logger.info("Using backend logic directly (single deployment)")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    ) 