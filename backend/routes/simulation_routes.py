# Simulation routes for SIP Simulator
from flask import Blueprint, request, jsonify
from datetime import datetime
import traceback
from services.simulation_service import SimulationService
from services.portfolio_service import PortfolioService

simulation_bp = Blueprint('simulation', __name__)
simulation_service = SimulationService()
portfolio_service = PortfolioService()

@simulation_bp.route('/simulate', methods=['POST'])
def simulate_sip():
    """Main SIP simulation endpoint"""
    try:
        data = request.json
        funds_data = data.get('funds', [])
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
        
        # Convert funds data to the format expected by process_portfolio
        funds = {}
        for fund in funds_data:
            funds[fund['fund_name']] = {
                'scheme_code': fund['scheme_code'],
                'sip_amount': fund['sip_amount']
            }
        
        result = portfolio_service.process_portfolio(funds, start_date, end_date)
        return jsonify({"success": True, "data": result})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "traceback": traceback.format_exc()}), 500

@simulation_bp.route('/cumulative-performance', methods=['POST'])
def cumulative_performance():
    """Get cumulative performance data for portfolio vs benchmark"""
    try:
        data = request.json
        funds_data = data.get('funds', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not funds_data:
            return jsonify({'success': False, 'error': 'No funds provided'})
        
        result = simulation_service.get_cumulative_performance(funds_data, start_date, end_date)
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@simulation_bp.route('/benchmark', methods=['POST'])
def benchmark_sip():
    """Compare portfolio with Nifty 50 benchmark"""
    try:
        data = request.json
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        sip_amount = data.get('sip_amount', 10000)
        
        result = simulation_service.benchmark_comparison(start_date, end_date, sip_amount)
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@simulation_bp.route('/step-up-sip', methods=['POST'])
def step_up_sip():
    """Simulate step-up SIP with annual increases"""
    try:
        data = request.get_json()
        funds = data.get('funds', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        step_up_percentage = data.get('step_up_percentage', 10)
        
        if not funds:
            return jsonify({'success': False, 'error': 'No funds provided'})
        
        result = simulation_service.simulate_step_up_sip(funds, start_date, end_date, step_up_percentage)
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 