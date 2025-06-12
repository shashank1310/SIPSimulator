# Portfolio service for SIP Simulator
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.data_generator import generate_mock_nav_data, simulate_sip_investment
from utils.calculations import calculate_cagr, calculate_xirr

class PortfolioService:
    def __init__(self):
        pass
    
    def process_portfolio(self, funds, start_date, end_date):
        """Process portfolio simulation for multiple funds"""
        try:
            # Use parallel processing for better performance
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_fund = {
                    executor.submit(self._process_single_fund, fund_name, fund_data, start_date, end_date): fund_name
                    for fund_name, fund_data in funds.items()
                }
                
                fund_results = []
                for future in as_completed(future_to_fund):
                    fund_name = future_to_fund[future]
                    try:
                        result = future.result()
                        if result:
                            fund_results.append(result)
                    except Exception as e:
                        print(f"Error processing fund {fund_name}: {e}")
                        continue
            
            if not fund_results:
                raise Exception("No fund data could be processed")
            
            # Calculate portfolio summary
            portfolio_summary = self._calculate_portfolio_summary(fund_results, start_date, end_date)
            
            return {
                'portfolio_summary': portfolio_summary,
                'funds': fund_results
            }
            
        except Exception as e:
            print(f"Portfolio processing error: {e}")
            raise e
    
    def _process_single_fund(self, fund_name, fund_data, start_date, end_date):
        """Process a single fund's SIP simulation"""
        try:
            scheme_code = fund_data['scheme_code']
            sip_amount = fund_data['sip_amount']
            
            # Generate NAV data
            nav_data = generate_mock_nav_data(scheme_code, start_date, end_date)
            if not nav_data:
                return None
            
            # Simulate SIP investment
            investment_data = simulate_sip_investment(nav_data, sip_amount, start_date, end_date)
            if not investment_data:
                return None
            
            # Calculate metrics
            final_data = investment_data[-1]
            total_invested = final_data['invested']
            current_value = final_data['current_value']
            
            # Calculate returns
            absolute_return = ((current_value - total_invested) / total_invested) * 100
            
            # Calculate CAGR
            years = (end_date - start_date).days / 365.25
            cagr = calculate_cagr(total_invested, current_value, years)
            
            # Calculate XIRR
            cash_flows = []
            for item in investment_data:
                cash_flows.append({
                    'date': item['date'],
                    'amount': -sip_amount  # Negative for investment
                })
            # Add final value as positive cash flow
            cash_flows.append({
                'date': end_date.strftime('%Y-%m-%d'),
                'amount': current_value
            })
            
            xirr = calculate_xirr(cash_flows)
            
            return {
                'fund_name': fund_name,
                'scheme_code': scheme_code,
                'sip_amount': sip_amount,
                'invested': total_invested,
                'current_value': current_value,
                'return_pct': absolute_return,
                'cagr': cagr,
                'xirr': xirr,
                'monthly_data': investment_data
            }
            
        except Exception as e:
            print(f"Error processing fund {fund_name}: {e}")
            return None
    
    def _calculate_portfolio_summary(self, fund_results, start_date, end_date):
        """Calculate overall portfolio summary"""
        try:
            total_invested = sum(fund['invested'] for fund in fund_results)
            total_current_value = sum(fund['current_value'] for fund in fund_results)
            
            # Calculate portfolio returns
            absolute_return = ((total_current_value - total_invested) / total_invested) * 100
            
            # Calculate portfolio CAGR
            years = (end_date - start_date).days / 365.25
            cagr = calculate_cagr(total_invested, total_current_value, years)
            
            # Calculate portfolio XIRR (weighted average approach)
            total_sip = sum(fund['sip_amount'] for fund in fund_results)
            portfolio_xirr = None
            
            if fund_results:
                # Use weighted average of individual XIRRs
                valid_xirrs = [fund['xirr'] for fund in fund_results if fund['xirr'] is not None]
                if valid_xirrs:
                    weights = [fund['sip_amount'] / total_sip for fund in fund_results if fund['xirr'] is not None]
                    portfolio_xirr = sum(xirr * weight for xirr, weight in zip(valid_xirrs, weights))
            
            return {
                'total_invested': total_invested,
                'final_value': total_current_value,
                'absolute_return': absolute_return,
                'cagr': cagr,
                'xirr': portfolio_xirr
            }
            
        except Exception as e:
            print(f"Error calculating portfolio summary: {e}")
            return {
                'total_invested': 0,
                'final_value': 0,
                'absolute_return': 0,
                'cagr': 0,
                'xirr': None
            } 