# Analysis routes for SIP Simulator
from flask import Blueprint, request, jsonify
from services.risk_service import RiskService
from services.goal_service import GoalService

analysis_bp = Blueprint('analysis', __name__)
risk_service = RiskService()
goal_service = GoalService()

@analysis_bp.route('/risk-analysis', methods=['POST'])
def risk_analysis():
    """Calculate comprehensive risk analysis for selected funds"""
    try:
        data = request.get_json()
        funds = data.get('funds', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not funds:
            return jsonify({'success': False, 'error': 'No funds provided'})
        
        result = risk_service.analyze_portfolio_risk(funds, start_date, end_date)
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        print(f"Risk analysis error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@analysis_bp.route('/goal-planning', methods=['POST'])
def goal_planning():
    """Calculate SIP requirements for various financial goals"""
    try:
        data = request.get_json()
        
        result = goal_service.calculate_goal_requirements(data)
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        print(f"Goal planning error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500 