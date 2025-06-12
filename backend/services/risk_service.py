# Risk analysis service for SIP Simulator
from datetime import datetime
from utils.data_generator import generate_mock_nav_data, generate_nifty50_data
from utils.calculations import calculate_risk_metrics

class RiskService:
    def __init__(self):
        pass
    
    def analyze_portfolio_risk(self, funds, start_date, end_date):
        """Analyze risk metrics for a portfolio of funds"""
        try:
            individual_funds = []
            portfolio_data = []
            
            # Process each fund
            for fund in funds:
                fund_risk = self._calculate_fund_risk(fund, start_date, end_date)
                if fund_risk:
                    individual_funds.append(fund_risk)
            
            if not individual_funds:
                raise Exception("Could not calculate risk for any funds")
            
            # Calculate portfolio-level metrics (weighted average)
            portfolio_metrics = self._calculate_portfolio_risk_metrics(individual_funds, funds)
            
            # Get benchmark metrics
            benchmark_metrics = self._get_benchmark_risk_metrics(start_date, end_date)
            
            return {
                'portfolio_metrics': portfolio_metrics,
                'benchmark_metrics': benchmark_metrics,
                'individual_funds': individual_funds,
                'analysis_period': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
            
        except Exception as e:
            print(f"Risk analysis error: {e}")
            raise e
    
    def _calculate_fund_risk(self, fund, start_date, end_date):
        """Calculate risk metrics for a single fund"""
        try:
            # Generate NAV data
            nav_data = generate_mock_nav_data(fund['scheme_code'], start_date, end_date)
            if not nav_data:
                return None
            
            # Calculate risk metrics
            risk_metrics = calculate_risk_metrics(nav_data)
            
            return {
                'fund_name': fund['fund_name'],
                'scheme_code': fund['scheme_code'],
                'risk_metrics': risk_metrics
            }
            
        except Exception as e:
            print(f"Error calculating risk for fund {fund.get('fund_name', 'Unknown')}: {e}")
            return None
    
    def _calculate_portfolio_risk_metrics(self, individual_funds, funds):
        """Calculate portfolio-level risk metrics"""
        try:
            total_sip = sum(fund['sip_amount'] for fund in funds)
            
            # Calculate weighted averages
            weighted_volatility = 0
            weighted_sharpe = 0
            weighted_sortino = 0
            weighted_max_dd = 0
            weighted_beta = 0
            weighted_win_rate = 0
            
            for i, fund_risk in enumerate(individual_funds):
                weight = funds[i]['sip_amount'] / total_sip
                metrics = fund_risk['risk_metrics']
                
                weighted_volatility += metrics['annualized_volatility'] * weight
                weighted_sharpe += metrics['sharpe_ratio'] * weight
                weighted_sortino += metrics['sortino_ratio'] * weight
                weighted_max_dd += metrics['max_drawdown'] * weight
                weighted_beta += metrics['beta'] * weight
                weighted_win_rate += metrics['win_rate'] * weight
            
            return {
                'annualized_volatility': round(weighted_volatility, 2),
                'sharpe_ratio': round(weighted_sharpe, 2),
                'sortino_ratio': round(weighted_sortino, 2),
                'max_drawdown': round(weighted_max_dd, 2),
                'beta': round(weighted_beta, 2),
                'win_rate': round(weighted_win_rate, 2)
            }
            
        except Exception as e:
            print(f"Error calculating portfolio risk metrics: {e}")
            return {
                'annualized_volatility': 18.0,
                'sharpe_ratio': 0.6,
                'sortino_ratio': 0.8,
                'max_drawdown': -15.0,
                'beta': 1.0,
                'win_rate': 65.0
            }
    
    def _get_benchmark_risk_metrics(self, start_date, end_date):
        """Get risk metrics for benchmark (Nifty 50)"""
        try:
            nifty_data = generate_nifty50_data(start_date, end_date)
            if nifty_data:
                return calculate_risk_metrics(nifty_data)
            else:
                # Return default Nifty 50 metrics
                return {
                    'annualized_volatility': 16.0,
                    'sharpe_ratio': 0.7,
                    'sortino_ratio': 0.9,
                    'max_drawdown': -12.0,
                    'beta': 1.0,
                    'win_rate': 68.0
                }
                
        except Exception as e:
            print(f"Error calculating benchmark risk: {e}")
            return {
                'annualized_volatility': 16.0,
                'sharpe_ratio': 0.7,
                'sortino_ratio': 0.9,
                'max_drawdown': -12.0,
                'beta': 1.0,
                'win_rate': 68.0
            } 