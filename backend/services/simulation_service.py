# Simulation service for SIP Simulator
from datetime import datetime
from utils.data_generator import generate_mock_nav_data, generate_nifty50_data, simulate_sip_investment, generate_step_up_sip_data
from utils.calculations import calculate_cagr, calculate_xirr

class SimulationService:
    def __init__(self):
        pass
    
    def get_cumulative_performance(self, funds_data, start_date, end_date):
        """Get cumulative performance data for portfolio vs benchmark"""
        try:
            # Calculate total SIP amount
            total_sip_amount = sum(fund['sip_amount'] for fund in funds_data)
            
            # Generate portfolio data (combined)
            portfolio_data = self._generate_portfolio_cumulative_data(funds_data, start_date, end_date)
            
            # Generate Nifty 50 benchmark data
            nifty_data = self._generate_benchmark_cumulative_data(total_sip_amount, start_date, end_date)
            
            return {
                'portfolio': portfolio_data,
                'nifty50': nifty_data,
                'metadata': {
                    'fund_count': len(funds_data),
                    'total_sip_amount': total_sip_amount,
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
            
        except Exception as e:
            print(f"Error in cumulative performance: {e}")
            return {'portfolio': [], 'nifty50': [], 'metadata': {}}
    
    def _generate_portfolio_cumulative_data(self, funds_data, start_date, end_date):
        """Generate cumulative portfolio performance data"""
        try:
            # Simulate each fund and combine results
            combined_data = {}
            
            for fund in funds_data:
                nav_data = generate_mock_nav_data(fund['scheme_code'], start_date, end_date)
                if nav_data:
                    investment_data = simulate_sip_investment(nav_data, fund['sip_amount'], start_date, end_date)
                    
                    # Combine with other funds
                    for item in investment_data:
                        date = item['date']
                        if date not in combined_data:
                            combined_data[date] = {'invested': 0, 'current_value': 0}
                        
                        combined_data[date]['invested'] += item['invested']
                        combined_data[date]['current_value'] += item['current_value']
            
            # Convert to list format
            portfolio_data = []
            for date in sorted(combined_data.keys()):
                portfolio_data.append({
                    'date': date,
                    'invested': combined_data[date]['invested'],
                    'current_value': combined_data[date]['current_value']
                })
            
            return portfolio_data
            
        except Exception as e:
            print(f"Error generating portfolio cumulative data: {e}")
            return []
    
    def _generate_benchmark_cumulative_data(self, total_sip_amount, start_date, end_date):
        """Generate benchmark (Nifty 50) cumulative data"""
        try:
            nifty_nav_data = generate_nifty50_data(start_date, end_date)
            if nifty_nav_data:
                return simulate_sip_investment(nifty_nav_data, total_sip_amount, start_date, end_date)
            return []
            
        except Exception as e:
            print(f"Error generating benchmark data: {e}")
            return []
    
    def benchmark_comparison(self, start_date, end_date, sip_amount):
        """Compare SIP with Nifty 50 benchmark"""
        try:
            # Generate Nifty 50 data
            nifty_nav_data = generate_nifty50_data(start_date, end_date)
            if not nifty_nav_data:
                raise Exception("Could not generate Nifty 50 data")
            
            # Simulate SIP investment in Nifty 50
            investment_data = simulate_sip_investment(nifty_nav_data, sip_amount, start_date, end_date)
            
            if not investment_data:
                raise Exception("Could not simulate Nifty 50 investment")
            
            # Calculate summary metrics
            final_data = investment_data[-1]
            total_invested = final_data['invested']
            final_value = final_data['current_value']
            
            # Calculate returns
            absolute_return = ((final_value - total_invested) / total_invested) * 100
            
            # Calculate CAGR
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            years = (end_dt - start_dt).days / 365.25
            cagr = calculate_cagr(total_invested, final_value, years)
            
            # Calculate XIRR
            cash_flows = []
            for item in investment_data:
                cash_flows.append({
                    'date': item['date'],
                    'amount': -sip_amount  # Negative for investment
                })
            # Add final value as positive cash flow
            cash_flows.append({
                'date': end_date,
                'amount': final_value
            })
            
            xirr = calculate_xirr(cash_flows)
            
            return {
                'portfolio_summary': {
                    'total_invested': total_invested,
                    'final_value': final_value,
                    'absolute_return': absolute_return,
                    'cagr': cagr,
                    'xirr': xirr
                },
                'monthly_data': investment_data
            }
            
        except Exception as e:
            print(f"Benchmark comparison error: {e}")
            raise e
    
    def simulate_step_up_sip(self, funds, start_date, end_date, step_up_percentage):
        """Simulate step-up SIP with annual increases"""
        try:
            portfolio_results = []
            portfolio_summary = {
                'total_invested': 0,
                'final_value': 0,
                'absolute_return': 0
            }
            
            # Calculate regular SIP comparison
            total_regular_sip = sum(fund['sip_amount'] for fund in funds)
            regular_sip_data = self._simulate_regular_sip_for_comparison(total_regular_sip, start_date, end_date)
            
            # Process each fund
            for fund in funds:
                nav_data = generate_mock_nav_data(fund['scheme_code'], start_date, end_date)
                if nav_data:
                    step_up_data = generate_step_up_sip_data(
                        nav_data, fund['sip_amount'], step_up_percentage, start_date, end_date
                    )
                    
                    if step_up_data:
                        final_data = step_up_data[-1]
                        
                        fund_result = {
                            'fund_name': fund['fund_name'],
                            'scheme_code': fund['scheme_code'],
                            'initial_sip': fund['sip_amount'],
                            'final_sip': final_data['sip_amount'],
                            'invested': final_data['invested'],
                            'current_value': final_data['current_value'],
                            'return_pct': ((final_data['current_value'] - final_data['invested']) / final_data['invested']) * 100,
                            'monthly_data': step_up_data
                        }
                        
                        portfolio_results.append(fund_result)
                        portfolio_summary['total_invested'] += final_data['invested']
                        portfolio_summary['final_value'] += final_data['current_value']
            
            # Calculate portfolio return
            if portfolio_summary['total_invested'] > 0:
                portfolio_summary['absolute_return'] = (
                    (portfolio_summary['final_value'] - portfolio_summary['total_invested']) / 
                    portfolio_summary['total_invested']
                ) * 100
            
            return {
                'funds': portfolio_results,
                'portfolio_summary': portfolio_summary,
                'step_up_details': {
                    'annual_increase': step_up_percentage
                },
                'comparison': {
                    'regular_sip': regular_sip_data
                }
            }
            
        except Exception as e:
            print(f"Step-up SIP simulation error: {e}")
            raise e
    
    def _simulate_regular_sip_for_comparison(self, total_sip_amount, start_date, end_date):
        """Simulate regular SIP for comparison with step-up SIP"""
        try:
            # Use Nifty 50 as benchmark for regular SIP
            nifty_data = generate_nifty50_data(start_date, end_date)
            if nifty_data:
                investment_data = simulate_sip_investment(nifty_data, total_sip_amount, start_date, end_date)
                if investment_data:
                    final_data = investment_data[-1]
                    return {
                        'total_invested': final_data['invested'],
                        'final_value': final_data['current_value'],
                        'return_percentage': ((final_data['current_value'] - final_data['invested']) / final_data['invested']) * 100
                    }
            
            return {
                'total_invested': 0,
                'final_value': 0,
                'return_percentage': 0
            }
            
        except Exception as e:
            print(f"Regular SIP comparison error: {e}")
            return {
                'total_invested': 0,
                'final_value': 0,
                'return_percentage': 0
            } 