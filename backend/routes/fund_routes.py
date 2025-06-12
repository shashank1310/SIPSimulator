# Fund routes for SIP Simulator
from flask import Blueprint, request, jsonify
from data.fund_data import search_funds, get_fund_list

fund_bp = Blueprint('fund', __name__)

@fund_bp.route('/search-funds', methods=['GET'])
def search_funds_endpoint():
    """Search for mutual funds by name or code"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query or len(query) < 2:
            return jsonify({'success': True, 'funds': []})
        
        results = search_funds(query)
        return jsonify({'success': True, 'funds': results})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/funds', methods=['GET'])
def get_all_funds():
    """Get all available funds"""
    try:
        funds = get_fund_list()
        return jsonify({'success': True, 'funds': funds})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 