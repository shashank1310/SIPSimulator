# Main Flask application for SIP Simulator
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from config import DEBUG, HOST, PORT

# Import route blueprints
from routes.simulation_routes import simulation_bp
from routes.analysis_routes import analysis_bp
from routes.fund_routes import fund_bp

# Create Flask app
app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(simulation_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')
app.register_blueprint(fund_bp, url_prefix='/api')

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'SIP Simulator API is running',
        'version': '2.0',
        'features': [
            'SIP Simulation',
            'Risk Analysis',
            'Goal Planning',
            'Step-up SIP',
            'Fund Comparison',
            'Benchmark Comparison'
        ]
    })

@app.route('/health')
def health_check():
    """Detailed health check"""
    return jsonify({
        'status': 'healthy',
        'api_version': '2.0',
        'modules': {
            'simulation': 'active',
            'analysis': 'active',
            'fund_search': 'active'
        }
    })

if __name__ == '__main__':
    print("🚀 Starting SIP Simulator API v2.0...")
    print(f"📊 Available endpoints:")
    print(f"   • POST /api/simulate - SIP simulation")
    print(f"   • POST /api/cumulative-performance - Portfolio vs benchmark")
    print(f"   • POST /api/benchmark - Nifty 50 comparison")
    print(f"   • POST /api/step-up-sip - Step-up SIP simulation")
    print(f"   • POST /api/risk-analysis - Risk metrics")
    print(f"   • POST /api/goal-planning - Financial goal planning")
    print(f"   • GET /api/search-funds - Fund search")
    print(f"   • GET /api/funds - All funds")
    print(f"🌐 Server running on http://{HOST}:{PORT}")
    
    app.run(debug=DEBUG, host=HOST, port=PORT) 