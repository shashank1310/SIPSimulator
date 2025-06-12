# Data generation utilities for SIP Simulator
import pandas as pd
import numpy as np
import random
import requests
from datetime import datetime, timedelta
from config import API_TIMEOUT

def generate_mock_nav_data(scheme_code, start_date, end_date, sip_amount=10000):
    """Generate mock NAV data for a fund"""
    try:
        # Try to fetch real data first
        real_data = fetch_real_nav_data(scheme_code, start_date, end_date)
        if real_data:
            return real_data
        
        # Generate mock data if real data not available
        return generate_fallback_nav_data(scheme_code, start_date, end_date, sip_amount)
        
    except Exception as e:
        print(f"Error generating NAV data for {scheme_code}: {e}")
        return generate_fallback_nav_data(scheme_code, start_date, end_date, sip_amount)

def fetch_real_nav_data(scheme_code, start_date, end_date):
    """Fetch real NAV data from API"""
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            nav_data = data.get('data', [])
            
            if not nav_data:
                return None
            
            # Convert to our format
            processed_data = []
            start_dt = datetime.strptime(start_date, '%Y-%m-%d') if isinstance(start_date, str) else start_date
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') if isinstance(end_date, str) else end_date
            
            for item in nav_data:
                nav_date = datetime.strptime(item['date'], '%d-%m-%Y')
                if start_dt <= nav_date <= end_dt:
                    processed_data.append({
                        'date': nav_date.strftime('%Y-%m-%d'),
                        'nav': float(item['nav'])
                    })
            
            # Sort by date
            processed_data.sort(key=lambda x: x['date'])
            
            if len(processed_data) >= 10:  # Need minimum data points
                return processed_data
                
    except Exception as e:
        print(f"Error fetching NAV for {scheme_code}: {e}")
    
    return None

def generate_fallback_nav_data(scheme_code, start_date, end_date, sip_amount=10000):
    """Generate optimized fallback NAV data"""
    print(f"Using optimized fallback NAV data for scheme {scheme_code}")
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d') if isinstance(start_date, str) else start_date
    end_dt = datetime.strptime(end_date, '%Y-%m-%d') if isinstance(end_date, str) else end_date
    
    # Generate monthly data points
    current_date = start_dt.replace(day=1)  # Start from first day of month
    nav_data = []
    
    # Base NAV (realistic range for Indian mutual funds)
    base_nav = random.uniform(15, 150)
    current_nav = base_nav
    
    # Market volatility parameters
    annual_return = random.uniform(0.08, 0.18)  # 8-18% annual return
    monthly_volatility = random.uniform(0.03, 0.08)  # 3-8% monthly volatility
    
    while current_date <= end_dt:
        # Generate monthly return with some randomness
        monthly_return = (annual_return / 12) + random.gauss(0, monthly_volatility)
        current_nav *= (1 + monthly_return)
        
        nav_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'nav': round(current_nav, 4)
        })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return nav_data

def generate_nifty50_data(start_date, end_date, sip_amount=10000):
    """Generate Nifty 50 benchmark data"""
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d') if isinstance(start_date, str) else start_date
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') if isinstance(end_date, str) else end_date
        
        # Generate monthly data points
        current_date = start_dt.replace(day=1)
        nav_data = []
        
        # Nifty 50 base value (realistic range)
        base_value = random.uniform(10000, 20000)
        current_value = base_value
        
        # Nifty 50 historical parameters (more conservative)
        annual_return = random.uniform(0.10, 0.14)  # 10-14% annual return
        monthly_volatility = random.uniform(0.04, 0.07)  # 4-7% monthly volatility
        
        while current_date <= end_dt:
            # Generate monthly return
            monthly_return = (annual_return / 12) + random.gauss(0, monthly_volatility)
            current_value *= (1 + monthly_return)
            
            nav_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'nav': round(current_value, 2)
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return nav_data
        
    except Exception as e:
        print(f"Error generating Nifty 50 data: {e}")
        return []

def simulate_sip_investment(nav_data, sip_amount, start_date, end_date):
    """Simulate SIP investment based on NAV data"""
    try:
        if not nav_data:
            return []
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d') if isinstance(start_date, str) else start_date
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') if isinstance(end_date, str) else end_date
        
        # Convert NAV data to DataFrame
        df = pd.DataFrame(nav_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Generate monthly SIP dates
        sip_dates = []
        current_date = start_dt.replace(day=1)  # SIP on 1st of each month
        
        while current_date <= end_dt:
            sip_dates.append(current_date)
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Simulate SIP investments
        investment_data = []
        total_invested = 0
        total_units = 0
        
        for sip_date in sip_dates:
            # Find closest NAV date
            nav_row = df[df['date'] <= sip_date].tail(1)
            
            if not nav_row.empty:
                nav_value = nav_row.iloc[0]['nav']
                units_purchased = sip_amount / nav_value
                total_units += units_purchased
                total_invested += sip_amount
                
                # Current value calculation
                current_nav = df.iloc[-1]['nav']  # Latest NAV
                current_value = total_units * current_nav
                
                investment_data.append({
                    'date': sip_date.strftime('%Y-%m-%d'),
                    'nav': nav_value,
                    'invested': total_invested,
                    'units': total_units,
                    'current_value': current_value
                })
        
        return investment_data
        
    except Exception as e:
        print(f"Error simulating SIP investment: {e}")
        return []

def generate_step_up_sip_data(nav_data, initial_sip, step_up_percentage, start_date, end_date):
    """Generate step-up SIP investment data"""
    try:
        if not nav_data:
            return []
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d') if isinstance(start_date, str) else start_date
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') if isinstance(end_date, str) else end_date
        
        # Convert NAV data to DataFrame
        df = pd.DataFrame(nav_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Generate monthly SIP dates
        sip_dates = []
        current_date = start_dt.replace(day=1)
        
        while current_date <= end_dt:
            sip_dates.append(current_date)
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Simulate step-up SIP
        investment_data = []
        total_invested = 0
        total_units = 0
        current_sip = initial_sip
        year_start = start_dt.year
        
        for i, sip_date in enumerate(sip_dates):
            # Increase SIP amount annually
            if sip_date.year > year_start:
                years_passed = sip_date.year - year_start
                current_sip = initial_sip * ((1 + step_up_percentage/100) ** years_passed)
            
            # Find closest NAV date
            nav_row = df[df['date'] <= sip_date].tail(1)
            
            if not nav_row.empty:
                nav_value = nav_row.iloc[0]['nav']
                units_purchased = current_sip / nav_value
                total_units += units_purchased
                total_invested += current_sip
                
                # Current value calculation
                current_nav = df.iloc[-1]['nav']
                current_value = total_units * current_nav
                
                investment_data.append({
                    'date': sip_date.strftime('%Y-%m-%d'),
                    'nav': nav_value,
                    'sip_amount': current_sip,
                    'invested': total_invested,
                    'units': total_units,
                    'current_value': current_value
                })
        
        return investment_data
        
    except Exception as e:
        print(f"Error generating step-up SIP data: {e}")
        return [] 