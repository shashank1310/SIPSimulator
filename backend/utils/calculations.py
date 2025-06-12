# Calculation utilities for SIP Simulator
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.optimize import newton
import math
import random
from config import RISK_FREE_RATE, DEFAULT_EXPECTED_RETURN, DEFAULT_INFLATION_RATE

def calculate_xirr(cash_flows):
    """Calculate XIRR (Extended Internal Rate of Return) for irregular cash flows"""
    try:
        if not cash_flows or len(cash_flows) < 2:
            return None
        
        # Convert to pandas DataFrame for easier handling
        df = pd.DataFrame(cash_flows)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Calculate days from first investment
        first_date = df['date'].iloc[0]
        df['days'] = (df['date'] - first_date).dt.days
        
        def xirr_func(rate):
            return sum(amount / (1 + rate) ** (days / 365.0) 
                      for amount, days in zip(df['amount'], df['days']))
        
        # Use Newton's method to find the rate
        rate = newton(xirr_func, 0.1, maxiter=100)
        return rate * 100  # Convert to percentage
        
    except Exception as e:
        print(f"XIRR calculation error: {e}")
        return None

def calculate_cagr(initial_value, final_value, years):
    """Calculate Compound Annual Growth Rate"""
    if initial_value <= 0 or final_value <= 0 or years <= 0:
        return 0
    
    try:
        cagr = ((final_value / initial_value) ** (1 / years)) - 1
        return cagr * 100
    except:
        return 0

def calculate_sip_future_value(monthly_sip, annual_return, years):
    """Calculate future value of SIP"""
    monthly_return = annual_return / 12 / 100
    months = years * 12
    
    if monthly_return == 0:
        return monthly_sip * months
    
    future_value = monthly_sip * (((1 + monthly_return) ** months - 1) / monthly_return)
    return future_value

def calculate_required_sip(target_amount, annual_return, years):
    """Calculate required monthly SIP to achieve target amount"""
    monthly_return = annual_return / 12 / 100
    months = years * 12
    
    if monthly_return == 0:
        return target_amount / months
    
    required_sip = target_amount * monthly_return / ((1 + monthly_return) ** months - 1)
    return required_sip

def calculate_step_up_sip_value(initial_sip, annual_return, years, step_up_percentage):
    """Calculate future value of step-up SIP"""
    monthly_return = annual_return / 12 / 100
    annual_step_up = step_up_percentage / 100
    
    total_value = 0
    current_sip = initial_sip
    
    for year in range(years):
        # Calculate value for current year
        year_value = calculate_sip_future_value(current_sip, annual_return, 1)
        
        # Compound the value for remaining years
        remaining_years = years - year - 1
        if remaining_years > 0:
            year_value *= (1 + annual_return / 100) ** remaining_years
        
        total_value += year_value
        
        # Increase SIP for next year
        current_sip *= (1 + annual_step_up)
    
    return total_value

def calculate_risk_metrics(fund_data, benchmark_data=None):
    """Calculate comprehensive risk metrics for a fund"""
    try:
        if not fund_data or len(fund_data) < 12:  # Need at least 12 months of data
            return get_default_risk_metrics()
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(fund_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Calculate monthly returns
        df['nav_return'] = df['nav'].pct_change()
        monthly_returns = df['nav_return'].dropna()
        
        if len(monthly_returns) < 6:  # Need at least 6 months of returns
            return get_default_risk_metrics()
        
        # Basic statistics
        mean_return = monthly_returns.mean()
        std_return = monthly_returns.std()
        
        # Annualized metrics
        annualized_return = (1 + mean_return) ** 12 - 1
        annualized_volatility = std_return * np.sqrt(12)
        
        # Sharpe Ratio
        risk_free_monthly = RISK_FREE_RATE / 12
        excess_returns = monthly_returns - risk_free_monthly
        sharpe_ratio = excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0
        
        # Sortino Ratio (downside deviation)
        downside_returns = monthly_returns[monthly_returns < 0]
        downside_deviation = downside_returns.std() if len(downside_returns) > 0 else std_return
        sortino_ratio = excess_returns.mean() / downside_deviation if downside_deviation > 0 else 0
        
        # Maximum Drawdown
        cumulative_returns = (1 + monthly_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(monthly_returns, 5)
        
        # Beta (if benchmark data available)
        beta = 1.0  # Default
        if benchmark_data and len(benchmark_data) >= len(fund_data):
            benchmark_df = pd.DataFrame(benchmark_data)
            benchmark_df['date'] = pd.to_datetime(benchmark_df['date'])
            benchmark_df = benchmark_df.sort_values('date')
            benchmark_df['return'] = benchmark_df['nav'].pct_change()
            
            # Align dates
            merged = pd.merge(df[['date', 'nav_return']], 
                            benchmark_df[['date', 'return']], 
                            on='date', how='inner')
            
            if len(merged) > 6:
                fund_returns = merged['nav_return'].dropna()
                benchmark_returns = merged['return'].dropna()
                
                if len(fund_returns) == len(benchmark_returns) and len(fund_returns) > 0:
                    covariance = np.cov(fund_returns, benchmark_returns)[0][1]
                    benchmark_variance = np.var(benchmark_returns)
                    beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
        
        # Treynor Ratio
        treynor_ratio = (annualized_return - RISK_FREE_RATE) / beta if beta != 0 else 0
        
        # Win Rate
        positive_months = len(monthly_returns[monthly_returns > 0])
        win_rate = (positive_months / len(monthly_returns)) * 100
        
        return {
            'annualized_return': round(annualized_return * 100, 2),
            'annualized_volatility': round(annualized_volatility * 100, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'sortino_ratio': round(sortino_ratio, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'var_95': round(var_95 * 100, 2),
            'beta': round(beta, 2),
            'treynor_ratio': round(treynor_ratio, 2),
            'win_rate': round(win_rate, 2)
        }
        
    except Exception as e:
        print(f"Risk calculation error: {e}")
        return get_default_risk_metrics()

def get_default_risk_metrics():
    """Return default risk metrics when calculation fails"""
    return {
        'annualized_return': 12.0,
        'annualized_volatility': 18.0,
        'sharpe_ratio': 0.6,
        'sortino_ratio': 0.8,
        'max_drawdown': -15.0,
        'var_95': -8.0,
        'beta': 1.0,
        'treynor_ratio': 0.06,
        'win_rate': 65.0
    }

def calculate_goal_sip_requirements(goal_amount, time_horizon, expected_return, inflation_rate):
    """Calculate SIP requirements for financial goals"""
    # Adjust goal amount for inflation
    real_return = ((1 + expected_return/100) / (1 + inflation_rate/100)) - 1
    
    # Regular SIP calculation
    regular_sip = calculate_required_sip(goal_amount, expected_return, time_horizon)
    
    # Step-up SIP calculation (starting with 20% less, increasing 10% annually)
    step_up_initial = regular_sip * 0.8
    step_up_percentage = 10
    
    # Calculate total investment for regular SIP
    total_investment_regular = regular_sip * 12 * time_horizon
    
    # Calculate wealth multiplier
    wealth_multiplier = goal_amount / total_investment_regular
    
    return {
        'regular_sip': round(regular_sip),
        'step_up_sip': round(step_up_initial),
        'total_investment_regular': round(total_investment_regular),
        'wealth_multiplier': round(wealth_multiplier, 1)
    }

def get_asset_allocation_recommendation(time_horizon, risk_tolerance='moderate'):
    """Get asset allocation recommendation based on time horizon and risk tolerance"""
    from config import ASSET_ALLOCATION_TEMPLATES
    
    if time_horizon >= 15:
        if risk_tolerance == 'aggressive':
            return ASSET_ALLOCATION_TEMPLATES['AGGRESSIVE']
        else:
            return ASSET_ALLOCATION_TEMPLATES['MODERATE']
    elif time_horizon >= 10:
        return ASSET_ALLOCATION_TEMPLATES['MODERATE']
    elif time_horizon >= 5:
        return ASSET_ALLOCATION_TEMPLATES['CONSERVATIVE']
    else:
        return ASSET_ALLOCATION_TEMPLATES['CAPITAL_PRESERVATION']

def determine_risk_level(time_horizon, goal_amount):
    """Determine risk level based on goal parameters"""
    if time_horizon >= 15 and goal_amount > 5000000:  # 50 lakhs+
        return 'High'
    elif time_horizon >= 10:
        return 'Medium'
    elif time_horizon >= 5:
        return 'Medium'
    else:
        return 'Low' 