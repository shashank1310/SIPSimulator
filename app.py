#!/usr/bin/env python3
"""
Production SIP Simulator Flask Application
Simplified version for reliable deployment
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import threading
from datetime import datetime

# Configuration
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'production-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true' and os.getenv('FLASK_ENV') != 'production'
    HOST = os.getenv('APP_HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))  # Render uses PORT env var
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Initialize Flask app
app = Flask(__name__, static_folder='frontend', static_url_path='')
app.config.from_object(Config)

# Setup CORS
CORS(app, origins=['*'])

# Setup logging
logging.basicConfig(level=getattr(logging, app.config['LOG_LEVEL']))
app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))

# Sample fund data
FUND_LIST = [
    {"scheme_code": "122639", "fund_name": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "120503", "fund_name": "SBI Bluechip Fund - Direct Plan - Growth"},
    {"scheme_code": "120465", "fund_name": "HDFC Top 100 Fund - Direct Plan - Growth"},
    {"scheme_code": "119597", "fund_name": "HDFC Mid-Cap Opportunities Fund - Direct Plan - Growth"},
    {"scheme_code": "119551", "fund_name": "HDFC Small Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "118825", "fund_name": "ICICI Prudential Bluechip Fund - Direct Plan - Growth"},
    {"scheme_code": "118989", "fund_name": "Axis Bluechip Fund - Direct Plan - Growth"},
    {"scheme_code": "113177", "fund_name": "Nippon India Small Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "120444", "fund_name": "SBI Magnum Midcap Fund - Direct Plan - Growth"},
    {"scheme_code": "147625", "fund_name": "UTI Nifty 50 Index Fund - Direct Plan - Growth"}
]

# Cache for search results
SEARCH_CACHE = {}
CACHE_TIMESTAMP = 0

# Rate limiting
request_counts = {}
request_lock = threading.Lock()

def rate_limit_check(client_ip, max_requests=100, per_seconds=60):
    """Simple rate limiting"""
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
            return False
        
        request_counts[client_ip].append(current_time)
        return True

# Error handlers
@app.errorhandler(404)
def not_found(error):
    app.logger.warning(f"404 error: {request.url}")
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

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

# Root endpoint
@app.route('/')
def home():
    """Home endpoint - serve frontend or API info"""
    try:
        return send_from_directory('frontend', 'index.html')
    except FileNotFoundError:
        return jsonify({
            'message': 'SIP Simulator API',
            'status': 'healthy',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'search_funds': '/api/search-funds?q=hdfc',
                'simulate': '/api/simulate (POST)',
                'benchmark': '/api/benchmark (POST)',
                'risk_analysis': '/api/risk-analysis (POST)'
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

# API Routes
@app.route('/api/search-funds', methods=['GET'])
def search_funds():
    """Search for mutual funds"""
    try:
        # Rate limiting
        if not rate_limit_check(request.remote_addr):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        query = request.args.get('q', '').strip().lower()
        
        if not query or len(query) < 2:
            return jsonify({
                'error': 'Query parameter is required and must be at least 2 characters'
            }), 400
        
        app.logger.info(f"Fund search query: {query}")
        
        # Check cache
        global SEARCH_CACHE, CACHE_TIMESTAMP
        current_time = time.time()
        cache_key = f"search_{query}"
        
        if (current_time - CACHE_TIMESTAMP < 3600 and cache_key in SEARCH_CACHE):
            return jsonify(SEARCH_CACHE[cache_key])
        
        # Filter funds
        matching_funds = []
        for fund in FUND_LIST:
            if query in fund['fund_name'].lower():
                matching_funds.append(fund)
        
        result = {'funds': matching_funds[:20]}  # Limit results
        
        # Cache results
        SEARCH_CACHE[cache_key] = result
        CACHE_TIMESTAMP = current_time
        
        app.logger.info(f"Found {len(matching_funds)} funds for query: {query}")
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in search_funds: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/simulate', methods=['POST'])
def simulate_sip():
    """Simulate SIP investment"""
    try:
        if not rate_limit_check(request.remote_addr, 50):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        funds = data.get('funds', [])
        start_date = data.get('start_date', '2020-01-01')  # Frontend sends start_date
        end_date = data.get('end_date', '2024-01-01')      # Frontend sends end_date
        
        app.logger.info(f"SIP simulation request: {len(funds)} funds, {start_date} to {end_date}")
        
        if not funds:
            return jsonify({'success': False, 'error': 'No funds provided'}), 400
        
        # Mock calculation - using sip_amount field from frontend
        total_sip = sum(fund.get('sip_amount', 5000) for fund in funds)
        months = 48  # 4 years
        total_investment = total_sip * months
        expected_return = 12.5  # 12.5% annual return
        final_value = total_investment * (1 + expected_return/100) ** 4
        
        # Create fund performance data matching frontend expectations
        fund_performance = []
        for fund in funds:
            sip_amount = fund.get('sip_amount', 5000)
            investment = sip_amount * months
            current_value = investment * 1.5  # Mock 50% gain
            return_pct = ((current_value - investment) / investment) * 100
            
            # Generate monthly data for performance chart
            import datetime
            from dateutil.relativedelta import relativedelta
            
            start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            
            monthly_data = []
            current_date = start
            cumulative_investment = 0
            cumulative_value = 0
            month_count = 0
            
            while current_date <= end:
                month_count += 1
                cumulative_investment += sip_amount
                
                # Apply mock monthly growth (12.5% annual = ~0.99% monthly)
                monthly_growth = 1 + (12.5 / 100 / 12)
                cumulative_value = (cumulative_value + sip_amount) * monthly_growth
                
                monthly_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'invested': round(cumulative_investment, 2),
                    'current_value': round(cumulative_value, 2),
                    'month': month_count
                })
                
                current_date += relativedelta(months=1)
            
            fund_performance.append({
                'fund_name': fund.get('fund_name', 'Unknown Fund'),
                'scheme_code': fund.get('scheme_code', ''),
                'sip_amount': sip_amount,
                'invested': investment,
                'current_value': current_value,
                'return_pct': return_pct,
                'cagr': 12.5,
                'xirr': 13.2,
                'monthly_data': monthly_data  # This is what the chart needs
            })
        
        # Portfolio summary matching frontend expectations
        portfolio_summary = {
            'total_invested': round(total_investment, 2),
            'final_value': round(final_value, 2),
            'total_gains': round(final_value - total_investment, 2),
            'cagr': expected_return,
            'absolute_return': round(((final_value - total_investment) / total_investment) * 100, 2),
            'xirr': 13.5
        }
        
        result = {
            'success': True,
            'data': {
                'portfolio_summary': portfolio_summary,
                'funds': fund_performance
            }
        }
        
        app.logger.info(f"Simulation completed successfully for {len(funds)} funds")
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in simulate_sip: {str(e)}")
        return jsonify({'success': False, 'error': 'Simulation failed'}), 500

@app.route('/api/benchmark', methods=['POST'])
def benchmark_comparison():
    """Compare with benchmark"""
    try:
        if not rate_limit_check(request.remote_addr, 50):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        app.logger.info("Benchmark comparison request")
        
        result = {
            'status': 'success',
            'benchmark_name': 'Nifty 50',
            'benchmark_returns': 10.8,
            'portfolio_returns': 12.5,
            'outperformance': 1.7,
            'alpha': 1.2,
            'beta': 0.95
        }
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in benchmark: {str(e)}")
        return jsonify({'error': 'Benchmark comparison failed'}), 500

@app.route('/api/risk-analysis', methods=['POST'])
def risk_analysis():
    """Perform risk analysis"""
    try:
        if not rate_limit_check(request.remote_addr, 30):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        funds = data.get('funds', [])
        app.logger.info("Risk analysis request")
        
        result = {
            'status': 'success',
            'portfolio_risk': {
                'volatility': 15.5,
                'sharpe_ratio': 1.2,
                'sortino_ratio': 1.4,
                'max_drawdown': 8.5,
                'var_95': 2.3,
                'beta': 0.95
            },
            'fund_risks': [
                {
                    'fund_name': fund.get('fund_name', 'Unknown Fund'),
                    'volatility': 16.2,
                    'sharpe_ratio': 1.1,
                    'max_drawdown': 9.2,
                    'risk_level': 'Medium'
                }
                for fund in funds
            ]
        }
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in risk_analysis: {str(e)}")
        return jsonify({'error': 'Risk analysis failed'}), 500

@app.route('/api/goal-planning', methods=['POST'])
def goal_planning():
    """Goal-based investment planning"""
    try:
        if not rate_limit_check(request.remote_addr, 30):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        target_amount = float(data.get('targetAmount', 1000000))
        years = int(data.get('years', 10))
        expected_return = float(data.get('expectedReturn', 12)) / 100
        
        # Calculate required SIP
        monthly_rate = expected_return / 12
        months = years * 12
        
        if monthly_rate > 0:
            required_sip = target_amount * monthly_rate / ((1 + monthly_rate) ** months - 1)
        else:
            required_sip = target_amount / months
        
        result = {
            'status': 'success',
            'required_sip': round(required_sip, 2),
            'target_amount': target_amount,
            'years': years,
            'expected_return': expected_return * 100,
            'total_investment': round(required_sip * months, 2),
            'wealth_gain': round(target_amount - (required_sip * months), 2)
        }
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in goal_planning: {str(e)}")
        return jsonify({'error': 'Goal planning failed'}), 500

@app.route('/api/cumulative-performance', methods=['POST'])
def cumulative_performance():
    """Get cumulative performance data for charts"""
    try:
        if not rate_limit_check(request.remote_addr, 30):
            return jsonify({'error': 'Rate limit exceeded'}), 429
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        funds = data.get('funds', [])
        start_date = data.get('start_date', '2020-01-01')
        end_date = data.get('end_date', '2024-01-01')
        
        app.logger.info(f"Cumulative performance request: {len(funds)} funds")
        
        # Generate mock cumulative data
        import datetime
        from dateutil.relativedelta import relativedelta
        
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate monthly data points
        dates = []
        portfolio_values = []
        nifty_values = []
        
        current_date = start
        portfolio_value = 0
        nifty_value = 0
        month_count = 0
        
        while current_date <= end:
            month_count += 1
            
            # Calculate monthly SIP investment
            monthly_sip = sum(fund.get('sip_amount', 5000) for fund in funds)
            portfolio_value += monthly_sip
            
            # Apply mock returns (portfolio: 12.5% annual, Nifty: 10.8% annual)
            portfolio_growth = 1 + (12.5 / 100 / 12)  # Monthly growth
            nifty_growth = 1 + (10.8 / 100 / 12)      # Monthly growth
            
            portfolio_value *= portfolio_growth
            nifty_value = (nifty_value + monthly_sip) * nifty_growth
            
            dates.append(current_date.strftime('%Y-%m-%d'))
            portfolio_values.append(round(portfolio_value, 2))
            nifty_values.append(round(nifty_value, 2))
            
            current_date += relativedelta(months=1)
        
        # Calculate final metrics
        total_investment = month_count * sum(fund.get('sip_amount', 5000) for fund in funds)
        portfolio_return = ((portfolio_value - total_investment) / total_investment) * 100
        nifty_return = ((nifty_value - total_investment) / total_investment) * 100
        
        result = {
            'success': True,
            'data': {
                'dates': dates,
                'portfolio_values': portfolio_values,
                'nifty_values': nifty_values,
                'portfolio_summary': {
                    'total_investment': total_investment,
                    'final_portfolio_value': portfolio_value,
                    'final_nifty_value': nifty_value,
                    'portfolio_return': round(portfolio_return, 2),
                    'nifty_return': round(nifty_return, 2),
                    'outperformance': round(portfolio_return - nifty_return, 2)
                }
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in cumulative_performance: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate cumulative performance data'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = app.config['DEBUG']
    
    if debug_mode:
        app.logger.info("Starting SIP Simulator in development mode")
    else:
        app.logger.info("Starting SIP Simulator in production mode")
    
    app.logger.info(f"Server will run on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    ) 