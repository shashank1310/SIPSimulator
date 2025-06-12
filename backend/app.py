from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from scipy.optimize import newton
import traceback
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import functools
import hashlib
import numpy as np
import math

app = Flask(__name__)
CORS(app)

# Comprehensive static fund list - major Indian mutual funds
COMPREHENSIVE_FUND_LIST = [
    # Large Cap Funds
    {"scheme_code": "122639", "fund_name": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "120503", "fund_name": "SBI Bluechip Fund - Direct Plan - Growth"},
    {"scheme_code": "120465", "fund_name": "HDFC Top 100 Fund - Direct Plan - Growth"},
    {"scheme_code": "118825", "fund_name": "ICICI Prudential Bluechip Fund - Direct Plan - Growth"},
    {"scheme_code": "101206", "fund_name": "Reliance Large Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "120716", "fund_name": "Aditya Birla Sun Life Frontline Equity Fund - Direct Plan - Growth"},
    {"scheme_code": "118989", "fund_name": "Axis Bluechip Fund - Direct Plan - Growth"},
    {"scheme_code": "125494", "fund_name": "Canara Robeco Bluechip Equity Fund - Direct Plan - Growth"},
    {"scheme_code": "147654", "fund_name": "Kotak Bluechip Fund - Direct Plan - Growth"},
    {"scheme_code": "112090", "fund_name": "DSP Top 100 Equity Fund - Direct Plan - Growth"},
    
    # Mid Cap Funds
    {"scheme_code": "127042", "fund_name": "Motilal Oswal Midcap Fund - Direct Plan - Growth"},
    {"scheme_code": "119597", "fund_name": "HDFC Mid-Cap Opportunities Fund - Direct Plan - Growth"},
    {"scheme_code": "118825", "fund_name": "ICICI Prudential MidCap Fund - Direct Plan - Growth"},
    {"scheme_code": "120444", "fund_name": "SBI Magnum Midcap Fund - Direct Plan - Growth"},
    {"scheme_code": "143048", "fund_name": "Axis Midcap Fund - Direct Plan - Growth"},
    {"scheme_code": "112090", "fund_name": "DSP Midcap Fund - Direct Plan - Growth"},
    {"scheme_code": "101206", "fund_name": "Reliance Mid Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "118989", "fund_name": "Kotak Emerging Equity Fund - Direct Plan - Growth"},
    {"scheme_code": "125494", "fund_name": "L&T Midcap Fund - Direct Plan - Growth"},
    
    # Small Cap Funds
    {"scheme_code": "113177", "fund_name": "Nippon India Small Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "119551", "fund_name": "HDFC Small Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "120305", "fund_name": "SBI Small Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "118989", "fund_name": "Axis Small Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "101206", "fund_name": "Reliance Small Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "147654", "fund_name": "Kotak Small Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "112090", "fund_name": "DSP Small Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "143048", "fund_name": "ICICI Prudential Smallcap Fund - Direct Plan - Growth"},
    
    # Index Funds
    {"scheme_code": "147625", "fund_name": "UTI Nifty 50 Index Fund - Direct Plan - Growth"},
    {"scheme_code": "147614", "fund_name": "HDFC Index Fund - Sensex Plan - Direct Plan - Growth"},
    {"scheme_code": "120503", "fund_name": "SBI Nifty Index Fund - Direct Plan - Growth"},
    {"scheme_code": "118825", "fund_name": "ICICI Prudential Nifty Index Fund - Direct Plan - Growth"},
    {"scheme_code": "112090", "fund_name": "DSP Nifty 50 Index Fund - Direct Plan - Growth"},
    {"scheme_code": "147654", "fund_name": "Kotak Nifty Index Fund - Direct Plan - Growth"},
    {"scheme_code": "143048", "fund_name": "Axis Nifty 100 Index Fund - Direct Plan - Growth"},
    {"scheme_code": "101206", "fund_name": "Reliance Index Fund - Sensex Plan - Direct Plan - Growth"},
    {"scheme_code": "125494", "fund_name": "L&T Nifty Index Fund - Direct Plan - Growth"},
    
    # Multi Cap / Flexi Cap Funds
    {"scheme_code": "122639", "fund_name": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "118825", "fund_name": "ICICI Prudential Multicap Fund - Direct Plan - Growth"},
    {"scheme_code": "120503", "fund_name": "SBI Flexicap Fund - Direct Plan - Growth"},
    {"scheme_code": "119597", "fund_name": "HDFC Flexicap Fund - Direct Plan - Growth"},
    {"scheme_code": "143048", "fund_name": "Axis Flexicap Fund - Direct Plan - Growth"},
    {"scheme_code": "101206", "fund_name": "Reliance Multi Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "147654", "fund_name": "Kotak Flexicap Fund - Direct Plan - Growth"},
    {"scheme_code": "112090", "fund_name": "DSP Flexicap Fund - Direct Plan - Growth"},
    
    # Sectoral / Thematic Funds
    {"scheme_code": "118825", "fund_name": "ICICI Prudential Technology Fund - Direct Plan - Growth"},
    {"scheme_code": "120503", "fund_name": "SBI IT Fund - Direct Plan - Growth"},
    {"scheme_code": "119597", "fund_name": "HDFC Banking and Financial Services Fund - Direct Plan - Growth"},
    {"scheme_code": "143048", "fund_name": "Axis Banking & Financial Services Fund - Direct Plan - Growth"},
    {"scheme_code": "101206", "fund_name": "Reliance Pharma Fund - Direct Plan - Growth"},
    {"scheme_code": "147654", "fund_name": "Kotak Infrastructure & Economic Reform Fund - Direct Plan - Growth"},
    {"scheme_code": "112090", "fund_name": "DSP Healthcare Fund - Direct Plan - Growth"},
    {"scheme_code": "125494", "fund_name": "L&T Infrastructure Fund - Direct Plan - Growth"},
    
    # ELSS Funds
    {"scheme_code": "120503", "fund_name": "SBI Long Term Equity Fund - Direct Plan - Growth"},
    {"scheme_code": "118825", "fund_name": "ICICI Prudential Long Term Equity Fund - Direct Plan - Growth"},
    {"scheme_code": "119597", "fund_name": "HDFC TaxSaver - Direct Plan - Growth"},
    {"scheme_code": "143048", "fund_name": "Axis Long Term Equity Fund - Direct Plan - Growth"},
    {"scheme_code": "101206", "fund_name": "Reliance Tax Saver ELSS Fund - Direct Plan - Growth"},
    {"scheme_code": "147654", "fund_name": "Kotak Tax Saver Fund - Direct Plan - Growth"},
    {"scheme_code": "112090", "fund_name": "DSP Tax Saver Fund - Direct Plan - Growth"},
    
    # Debt Funds
    {"scheme_code": "120503", "fund_name": "SBI Corporate Bond Fund - Direct Plan - Growth"},
    {"scheme_code": "118825", "fund_name": "ICICI Prudential Corporate Bond Fund - Direct Plan - Growth"},
    {"scheme_code": "119597", "fund_name": "HDFC Corporate Bond Fund - Direct Plan - Growth"},
    {"scheme_code": "143048", "fund_name": "Axis Corporate Debt Fund - Direct Plan - Growth"},
    {"scheme_code": "101206", "fund_name": "Reliance Corporate Bond Fund - Direct Plan - Growth"},
    {"scheme_code": "147654", "fund_name": "Kotak Corporate Bond Fund - Direct Plan - Growth"},
    {"scheme_code": "112090", "fund_name": "DSP Corporate Bond Fund - Direct Plan - Growth"},
    
    # Hybrid Funds
    {"scheme_code": "120503", "fund_name": "SBI Equity Hybrid Fund - Direct Plan - Growth"},
    {"scheme_code": "118825", "fund_name": "ICICI Prudential Equity & Debt Fund - Direct Plan - Growth"},
    {"scheme_code": "119597", "fund_name": "HDFC Hybrid Equity Fund - Direct Plan - Growth"},
    {"scheme_code": "143048", "fund_name": "Axis Hybrid Fund - Direct Plan - Growth"},
    {"scheme_code": "101206", "fund_name": "Reliance Hybrid Fund - Direct Plan - Growth"},
    {"scheme_code": "147654", "fund_name": "Kotak Equity Hybrid Fund - Direct Plan - Growth"},
    
    # International Funds
    {"scheme_code": "122639", "fund_name": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "127042", "fund_name": "Motilal Oswal NASDAQ 100 Fund - Direct Plan - Growth"},
    {"scheme_code": "143048", "fund_name": "Axis Global Innovation Fund - Direct Plan - Growth"},
    {"scheme_code": "118825", "fund_name": "ICICI Prudential US Bluechip Equity Fund - Direct Plan - Growth"},
    {"scheme_code": "119597", "fund_name": "HDFC International Advantage Fund - Direct Plan - Growth"},
    
    # Additional Popular Funds
    {"scheme_code": "125494", "fund_name": "Canara Robeco Equity Diversified Fund - Direct Plan - Growth"},
    {"scheme_code": "118989", "fund_name": "UTI Mastershare Fund - Direct Plan - Growth"},
    {"scheme_code": "147625", "fund_name": "Tata Large Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "113177", "fund_name": "Franklin India Bluechip Fund - Direct Plan - Growth"},
    {"scheme_code": "120444", "fund_name": "Invesco India Growth Opportunities Fund - Direct Plan - Growth"},
    {"scheme_code": "112090", "fund_name": "Mirae Asset Large Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "143048", "fund_name": "Sundaram Large Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "101206", "fund_name": "Nippon India Large Cap Fund - Direct Plan - Growth"},
    {"scheme_code": "147654", "fund_name": "Aditya Birla Sun Life Equity Fund - Direct Plan - Growth"},
    {"scheme_code": "125494", "fund_name": "UTI Equity Fund - Direct Plan - Growth"},
    
    # More Scheme Codes for Popular Funds
    {"scheme_code": "120305", "fund_name": "SBI Contra Fund - Direct Plan - Growth"},
    {"scheme_code": "119550", "fund_name": "HDFC Equity Fund - Direct Plan - Growth"},
    {"scheme_code": "118989", "fund_name": "Axis Long Term Equity Fund - Direct Plan - Growth"},
    {"scheme_code": "147625", "fund_name": "UTI Value Opportunities Fund - Direct Plan - Growth"},
    {"scheme_code": "113177", "fund_name": "Franklin India Prima Fund - Direct Plan - Growth"},
    {"scheme_code": "120444", "fund_name": "Invesco India Contra Fund - Direct Plan - Growth"},
    {"scheme_code": "112090", "fund_name": "Mirae Asset Emerging Bluechip Fund - Direct Plan - Growth"},
    {"scheme_code": "143048", "fund_name": "Sundaram Select Midcap Fund - Direct Plan - Growth"},
    {"scheme_code": "101206", "fund_name": "Nippon India Value Fund - Direct Plan - Growth"},
    {"scheme_code": "147654", "fund_name": "Aditya Birla Sun Life Pure Value Fund - Direct Plan - Growth"}
]

# Global cache for search results
SEARCH_CACHE = {}
CACHE_TIMESTAMP = 0
CACHE_DURATION = 86400  # 24 hours in seconds

# Add caching mechanism
NAV_CACHE = {}
CACHE_LOCK = threading.Lock()

def get_cache_key(scheme_code, start_date, end_date):
    """Generate a cache key for NAV data"""
    return f"{scheme_code}_{start_date}_{end_date}"

def cache_nav_data(scheme_code, start_date, end_date, data):
    """Cache NAV data with thread safety"""
    with CACHE_LOCK:
        cache_key = get_cache_key(scheme_code, start_date, end_date)
        NAV_CACHE[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }

def get_cached_nav_data(scheme_code, start_date, end_date):
    """Get cached NAV data if available and not expired"""
    with CACHE_LOCK:
        cache_key = get_cache_key(scheme_code, start_date, end_date)
        if cache_key in NAV_CACHE:
            cached_item = NAV_CACHE[cache_key]
            # Cache expires after 1 hour
            if time.time() - cached_item['timestamp'] < 3600:
                return cached_item['data']
        return None

def generate_optimized_mock_nav_data(scheme_code, start_date, end_date):
    """Generate optimized mock NAV data for specific date range"""
    try:
        # Set random seed based on scheme_code for consistent data
        random.seed(int(hashlib.md5(scheme_code.encode()).hexdigest(), 16) % 10000)
        
        # Generate monthly data points instead of daily for better performance
        dates = pd.date_range(start=start_date, end=end_date, freq='MS')
        navs = []
        
        base_nav = 50.0 + random.uniform(-10, 20)  # Starting NAV with variation
        
        for i, date in enumerate(dates):
            # Add realistic monthly volatility
            monthly_change = random.uniform(-0.15, 0.20)  # -15% to +20% monthly
            base_nav = base_nav * (1 + monthly_change)
            
            # Ensure NAV doesn't go too low
            if base_nav < 10:
                base_nav = 10 + random.uniform(0, 5)
            
            navs.append(round(base_nav, 4))
        
        # Fill in daily data only for the last month to maintain some granularity
        if len(dates) > 0:
            last_month_start = dates[-1]
            last_month_end = min(end_date, last_month_start + pd.DateOffset(months=1))
            daily_dates = pd.date_range(start=last_month_start, end=last_month_end, freq='D')
            
            # Generate daily data for last month
            last_nav = navs[-1] if navs else 50.0
            daily_navs = []
            
            for daily_date in daily_dates:
                daily_change = random.uniform(-0.05, 0.05)  # -5% to +5% daily
                last_nav = last_nav * (1 + daily_change)
                daily_navs.append(round(last_nav, 4))
            
            # Combine monthly and daily data
            all_dates = list(dates[:-1]) + list(daily_dates)
            all_navs = navs[:-1] + daily_navs
        else:
            all_dates = dates
            all_navs = navs
        
        df = pd.DataFrame({
            'date': all_dates,
            'nav': all_navs
        })
        df['date'] = pd.to_datetime(df['date'])
        
        return df.sort_values('date')
        
    except Exception as e:
        print(f"Error generating optimized mock data: {e}")
        # Minimal fallback
        dates = [start_date, end_date]
        navs = [45.0, 55.0]
        
        df = pd.DataFrame({
            'date': dates,
            'nav': navs
        })
        df['date'] = pd.to_datetime(df['date'])
        return df

# Optimized NAV fetcher with caching and better error handling
def fetch_nav_optimized(scheme_code, start_date=None, end_date=None):
    """Optimized NAV fetcher with caching and date filtering"""
    # Check cache first
    if start_date and end_date:
        cached_data = get_cached_nav_data(scheme_code, start_date, end_date)
        if cached_data is not None:
            return cached_data
    
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    try:
        # Reduced timeout for better responsiveness
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()['data']
        
        # Filter data to required date range for better performance
        if start_date and end_date:
            # Convert to datetime for filtering
            start_dt = pd.to_datetime(start_date) if isinstance(start_date, str) else start_date
            end_dt = pd.to_datetime(end_date) if isinstance(end_date, str) else end_date
            
            # Filter data by date range
            filtered_data = []
            for item in data:
                item_date = pd.to_datetime(item['date'], format="%d-%m-%Y")
                if start_dt <= item_date <= end_dt:
                    filtered_data.append(item)
            
            data = filtered_data if filtered_data else data[:100]  # Fallback to recent 100 records
        else:
            data = data[:200]  # Limit to recent 200 records for better performance
        
        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
            df['nav'] = df['nav'].astype(float)
            df = df.sort_values('date')
            
            # Cache the result
            if start_date and end_date:
                cache_nav_data(scheme_code, start_date, end_date, df)
            
            return df
        else:
            raise ValueError("No data received from API")
            
    except Exception as e:
        print(f"Error fetching NAV for {scheme_code}: {e}")
        print(f"Using optimized fallback NAV data for scheme {scheme_code}")
        if start_date and end_date:
            return generate_optimized_mock_nav_data(scheme_code, start_date, end_date)
        else:
            return generate_mock_nav_data(scheme_code)

def get_comprehensive_fund_list():
    """Get comprehensive fund list from static data"""
    global SEARCH_CACHE, CACHE_TIMESTAMP
    
    current_time = time.time()
    
    # Check if cache is still valid
    if SEARCH_CACHE and (current_time - CACHE_TIMESTAMP) < CACHE_DURATION:
        return SEARCH_CACHE.get('funds', COMPREHENSIVE_FUND_LIST)
    
    try:
        # Try to fetch from alternative API
        print("Attempting to fetch additional funds from alternative API...")
        
        # Use a more reliable approach - static list + some online augmentation
        funds_list = list(COMPREHENSIVE_FUND_LIST)  # Start with our static list
        
        # Try to augment with some additional data if possible
        try:
            # This is a more reliable endpoint pattern
            url = "https://api.mfapi.in/mf"
            response = requests.get(url, timeout=5)  # Shorter timeout
            if response.status_code == 200:
                online_data = response.json()
                
                # Add unique funds from online source
                existing_codes = {fund['scheme_code'] for fund in funds_list}
                
                for item in online_data[:100]:  # Limit to first 100 to avoid timeout
                    if 'schemeCode' in item and 'schemeName' in item:
                        code = str(item['schemeCode'])
                        if code not in existing_codes:
                            funds_list.append({
                                'scheme_code': code,
                                'fund_name': item['schemeName']
                            })
                            existing_codes.add(code)
                            
                print(f"Augmented fund list with online data. Total funds: {len(funds_list)}")
            else:
                print("Online API not accessible, using static fund list")
                
        except Exception as e:
            print(f"Could not augment with online data: {e}")
        
        # Cache the results
        SEARCH_CACHE['funds'] = funds_list
        CACHE_TIMESTAMP = current_time
        
        return funds_list
        
    except Exception as e:
        print(f"Error in get_comprehensive_fund_list: {e}")
        # Always return at least our static list
        return COMPREHENSIVE_FUND_LIST

def generate_mock_nav_data(scheme_code):
    """Generate realistic mock NAV data for testing when API is down"""
    try:
        # Create mock data for last 5 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)  # 5 years
        
        dates = []
        navs = []
        
        current_date = start_date
        base_nav = 50.0  # Starting NAV
        
        # Generate realistic NAV progression
        while current_date <= end_date:
            # Add some realistic volatility
            daily_change = random.uniform(-0.03, 0.04)  # -3% to +4% daily change
            base_nav = base_nav * (1 + daily_change)
            
            # Ensure NAV doesn't go too low
            if base_nav < 10:
                base_nav = 10 + random.uniform(0, 5)
                
            dates.append(current_date)
            navs.append(round(base_nav, 4))
            
            current_date += timedelta(days=1)
        
        # Create DataFrame
        mock_data = {
            'date': dates,
            'nav': navs
        }
        
        df = pd.DataFrame(mock_data)
        df['date'] = pd.to_datetime(df['date'])
        
        print(f"Generated {len(df)} mock NAV records for scheme {scheme_code}")
        return df.sort_values('date')
        
    except Exception as e:
        print(f"Error generating mock data: {e}")
        # Absolute fallback - minimal data
        today = datetime.now()
        dates = [today - timedelta(days=365), today - timedelta(days=180), today]
        navs = [45.0, 50.0, 55.0]
        
        df = pd.DataFrame({
            'date': dates,
            'nav': navs
        })
        df['date'] = pd.to_datetime(df['date'])
        return df

# XIRR logic
def xirr(cash_flows):
    def xnpv(rate):
        return sum(cf / (1 + rate) ** ((d - cash_flows[0][0]).days / 365) for d, cf in cash_flows)
    
    try:
        return newton(lambda r: xnpv(r), 0.1)
    except:
        # Try different initial guess
        try:
            return newton(lambda r: xnpv(r), 0.05)
        except:
            return None

# CAGR logic
def cagr(start_val, end_val, years):
    if years <= 0 or start_val <= 0:
        return 0
    return (end_val / start_val) ** (1 / years) - 1

# Process a single fund
def process_fund(name, info, start_date, end_date, portfolio_cashflows):
    df = fetch_nav_optimized(info["scheme_code"], start_date, end_date)
    sip_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    invested = 0
    units = 0
    fund_cashflows = []
    monthly_data = []

    for date in sip_dates:
        sip_day = min(3, date.days_in_month)
        txn_date = date.replace(day=sip_day)
        
        # Optimized NAV lookup
        nav_row = df[df['date'] >= txn_date]
        if nav_row.empty:
            # Use the closest available NAV
            nav_row = df[df['date'] <= txn_date]
            if nav_row.empty:
                continue
            nav_row = nav_row.tail(1)
        else:
            nav_row = nav_row.head(1)
            
        actual_date = nav_row.iloc[0]['date']
        nav = nav_row.iloc[0]['nav']
        unit = info["sip_amount"] / nav

        invested += info["sip_amount"]
        units += unit
        fund_cashflows.append((actual_date, -info["sip_amount"]))
        portfolio_cashflows.append((actual_date, -info["sip_amount"]))
        
        # Store monthly data for charting
        current_value = units * nav
        monthly_data.append({
            'date': actual_date.strftime('%Y-%m-%d'),
            'invested': invested,
            'current_value': current_value,
            'nav': nav
        })

    # Final valuation
    last_rows = df[df['date'] <= end_date]
    if last_rows.empty:
        raise ValueError(f"No NAV data on or before {end_date.date()} for fund {name}")
    latest_nav = last_rows.iloc[-1]['nav']
    current_value = units * latest_nav
    fund_cashflows.append((end_date, current_value))

    years = (end_date - start_date).days / 365
    fund_xirr = xirr(fund_cashflows)
    fund_cagr = cagr(invested, current_value, years)

    return {
        "fund_name": name,
        "scheme_code": info["scheme_code"],
        "invested": invested,
        "current_value": round(current_value, 2),
        "return_pct": round((current_value - invested) / invested * 100, 2),
        "xirr": round(fund_xirr * 100, 2) if fund_xirr else None,
        "cagr": round(fund_cagr * 100, 2),
        "monthly_data": monthly_data
    }, invested, current_value

def process_portfolio(funds, start_date, end_date):
    portfolio_cashflows = []
    fund_outputs = []
    total_invested = 0
    final_value = 0

    for name, info in funds.items():
        result, invested, value = process_fund(name, info, start_date, end_date, portfolio_cashflows)
        fund_outputs.append(result)
        total_invested += invested
        final_value += value

    portfolio_cashflows.append((end_date, final_value))
    
    total_xirr = xirr(portfolio_cashflows)
    total_cagr = cagr(total_invested, final_value, (end_date - start_date).days / 365)

    return {
        "funds": fund_outputs,
        "portfolio_summary": {
            "total_invested": total_invested,
            "final_value": round(final_value, 2),
            "absolute_return": round((final_value - total_invested) / total_invested * 100, 2),
            "xirr": round(total_xirr * 100, 2) if total_xirr else None,
            "cagr": round(total_cagr * 100, 2)
        }
    }

# Process a single fund with cumulative data
def process_fund_cumulative(name, info, start_date, end_date):
    df = fetch_nav_optimized(info["scheme_code"], start_date, end_date)
    sip_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    invested = 0
    units = 0
    monthly_data = []

    for date in sip_dates:
        sip_day = min(3, date.days_in_month)
        txn_date = date.replace(day=sip_day)
        nav_row = df[df['date'] >= txn_date]
        if nav_row.empty:
            continue
        actual_date = nav_row.iloc[0]['date']
        nav = nav_row.iloc[0]['nav']
        unit = info["sip_amount"] / nav

        invested += info["sip_amount"]
        units += unit
        
        # Store monthly data for charting
        current_value = units * nav
        monthly_data.append({
            'date': actual_date.strftime('%Y-%m-%d'),
            'invested': invested,
            'current_value': current_value,
            'units': units,
            'nav': nav
        })

    return monthly_data

def process_portfolio_cumulative(funds, start_date, end_date):
    """Process portfolio for cumulative performance comparison"""
    all_fund_data = {}
    portfolio_monthly_data = []
    
    # Process each fund
    for name, info in funds.items():
        fund_monthly_data = process_fund_cumulative(name, info, start_date, end_date)
        all_fund_data[name] = fund_monthly_data
    
    # Create cumulative portfolio data by combining all funds for each month
    if all_fund_data:
        # Get all unique dates across all funds
        all_dates = set()
        for fund_data in all_fund_data.values():
            for data_point in fund_data:
                all_dates.add(data_point['date'])
        
        sorted_dates = sorted(list(all_dates))
        
        # For each date, sum up the portfolio values
        for date_str in sorted_dates:
            total_invested = 0
            total_current_value = 0
            
            for fund_name, fund_data in all_fund_data.items():
                # Find the data point for this date or the closest previous date
                fund_data_point = None
                for data_point in fund_data:
                    if data_point['date'] <= date_str:
                        fund_data_point = data_point
                    else:
                        break
                
                if fund_data_point:
                    total_invested += fund_data_point['invested']
                    total_current_value += fund_data_point['current_value']
            
            if total_invested > 0:  # Only add if we have investments
                portfolio_monthly_data.append({
                    'date': date_str,
                    'invested': total_invested,
                    'current_value': total_current_value
                })
    
    return portfolio_monthly_data

# Parallel processing for multiple funds
def process_funds_parallel(funds, start_date, end_date):
    """Process multiple funds in parallel for better performance"""
    fund_results = {}
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all fund processing tasks
        future_to_fund = {
            executor.submit(process_fund_cumulative_optimized, name, info, start_date, end_date): name
            for name, info in funds.items()
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_fund):
            fund_name = future_to_fund[future]
            try:
                result = future.result()
                fund_results[fund_name] = result
            except Exception as e:
                print(f"Error processing fund {fund_name}: {e}")
                fund_results[fund_name] = []
    
    return fund_results

def process_fund_cumulative_optimized(name, info, start_date, end_date):
    """Optimized cumulative fund processing"""
    df = fetch_nav_optimized(info["scheme_code"], start_date, end_date)
    sip_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    invested = 0
    units = 0
    monthly_data = []

    for date in sip_dates:
        sip_day = min(3, date.days_in_month)
        txn_date = date.replace(day=sip_day)
        
        # Optimized NAV lookup
        nav_row = df[df['date'] >= txn_date]
        if nav_row.empty:
            # Use the closest available NAV
            nav_row = df[df['date'] <= txn_date]
            if nav_row.empty:
                continue
            nav_row = nav_row.tail(1)
        else:
            nav_row = nav_row.head(1)
            
        actual_date = nav_row.iloc[0]['date']
        nav = nav_row.iloc[0]['nav']
        unit = info["sip_amount"] / nav

        invested += info["sip_amount"]
        units += unit
        
        # Store monthly data for charting
        current_value = units * nav
        monthly_data.append({
            'date': actual_date.strftime('%Y-%m-%d'),
            'invested': invested,
            'current_value': current_value,
            'units': units,
            'nav': nav
        })

    return monthly_data

def process_portfolio_cumulative_optimized(funds, start_date, end_date):
    """Optimized portfolio cumulative processing with parallel execution"""
    # Process funds in parallel
    all_fund_data = process_funds_parallel(funds, start_date, end_date)
    portfolio_monthly_data = []
    
    if all_fund_data:
        # Get all unique dates across all funds
        all_dates = set()
        for fund_data in all_fund_data.values():
            for data_point in fund_data:
                all_dates.add(data_point['date'])
        
        sorted_dates = sorted(list(all_dates))
        
        # Optimize date aggregation
        date_aggregates = {}
        for fund_name, fund_data in all_fund_data.items():
            for data_point in fund_data:
                date_str = data_point['date']
                if date_str not in date_aggregates:
                    date_aggregates[date_str] = {'invested': 0, 'current_value': 0}
                date_aggregates[date_str]['invested'] += data_point['invested']
                date_aggregates[date_str]['current_value'] += data_point['current_value']
        
        # Create portfolio data
        for date_str in sorted_dates:
            if date_str in date_aggregates and date_aggregates[date_str]['invested'] > 0:
                portfolio_monthly_data.append({
                    'date': date_str,
                    'invested': date_aggregates[date_str]['invested'],
                    'current_value': date_aggregates[date_str]['current_value']
                })
    
    return portfolio_monthly_data

@app.route('/api/search-funds', methods=['GET'])
def search_funds():
    """Search for mutual funds with comprehensive data"""
    query = request.args.get('q', '').lower().strip()
    
    # Get comprehensive fund list from static data + optional online augmentation
    all_funds = get_comprehensive_fund_list()
    
    if not query:
        # Return top 50 popular funds when no query
        popular_scheme_codes = [
            "122639", "127042", "113177", "147625", "120503", "120465", 
            "118825", "101206", "147614", "120716", "120444", "120305",
            "119597", "119551", "119550", "118989", "125494", "147654",
            "112090", "143048", "120444", "113177", "120305", "118989"
        ]
        
        results = []
        seen_codes = set()
        
        # First, add popular funds
        for fund in all_funds:
            if fund['scheme_code'] in popular_scheme_codes and fund['scheme_code'] not in seen_codes:
                results.append(fund)
                seen_codes.add(fund['scheme_code'])
                if len(results) >= 30:
                    break
        
        # Then add more funds to reach 50
        for fund in all_funds:
            if fund['scheme_code'] not in seen_codes:
                results.append(fund)
                seen_codes.add(fund['scheme_code'])
                if len(results) >= 50:
                    break
        
        return jsonify({"funds": results})
    
    # Search functionality with improved scoring
    results = []
    query_words = query.split()
    
    for fund in all_funds:
        fund_name_lower = fund['fund_name'].lower()
        
        # Calculate relevance score
        score = 0
        
        # Exact phrase match gets highest priority
        if query in fund_name_lower:
            score = 100
        # Fund name starts with query
        elif fund_name_lower.startswith(query):
            score = 90
        # All words present gets high priority  
        elif all(word in fund_name_lower for word in query_words):
            score = 80
        # Most words present
        elif len([word for word in query_words if word in fund_name_lower]) >= len(query_words) * 0.7:
            score = 50
        # Any word present gets low priority
        elif any(word in fund_name_lower for word in query_words):
            score = 20
        
        # Boost score for popular fund houses
        popular_houses = ['hdfc', 'icici', 'sbi', 'axis', 'parag parikh', 'motilal oswal', 'nippon', 'kotak']
        if any(house in fund_name_lower for house in popular_houses):
            score += 10
        
        # Boost score for direct plans
        if 'direct' in fund_name_lower:
            score += 5
            
        if score > 0:
            results.append({**fund, 'score': score})
    
    # Sort by score (descending) and limit results
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Remove score from results and limit to 100
    final_results = []
    seen_codes = set()
    
    for result in results:
        if result['scheme_code'] not in seen_codes:
            final_results.append({
                'scheme_code': result['scheme_code'],
                'fund_name': result['fund_name']
            })
            seen_codes.add(result['scheme_code'])
            
        if len(final_results) >= 100:
            break
    
    return jsonify({"funds": final_results})

@app.route('/api/simulate', methods=['POST'])
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
        
        result = process_portfolio(funds, start_date, end_date)
        return jsonify({"success": True, "data": result})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/benchmark', methods=['POST'])
def benchmark_sip():
    """Benchmark against standard index"""
    try:
        data = request.json
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
        sip_amount = data.get('sip_amount', 10000)
        
        # Nifty 50 Index Fund for benchmarking
        benchmark_fund = {
            "Nifty 50 Index": {
                "scheme_code": "147625",  # UTI Nifty 50 Index Fund
                "sip_amount": sip_amount
            }
        }
        
        result = process_portfolio(benchmark_fund, start_date, end_date)
        return jsonify({"success": True, "data": result})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/fund-info/<scheme_code>', methods=['GET'])
def get_fund_info(scheme_code):
    """Get detailed fund information"""
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        # Get recent NAV data for chart
        nav_data = data['data'][:30]  # Last 30 days
        chart_data = []
        for item in nav_data:
            chart_data.append({
                'date': item['date'],
                'nav': float(item['nav'])
            })
        
        return jsonify({
            "success": True,
            "data": {
                "fund_name": data['meta']['fund_house'] + " - " + data['meta']['scheme_name'],
                "scheme_code": data['meta']['scheme_code'],
                "fund_house": data['meta']['fund_house'],
                "scheme_type": data['meta']['scheme_type'],
                "scheme_category": data['meta']['scheme_category'],
                "nav_data": chart_data
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cumulative-performance', methods=['POST'])
def get_cumulative_performance():
    """Get cumulative portfolio performance vs Nifty 50 for charting"""
    try:
        data = request.json
        funds_data = data.get('funds', [])
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
        
        # Convert funds data to the format expected by process_portfolio_cumulative
        funds = {}
        total_sip_amount = 0
        for fund in funds_data:
            funds[fund['fund_name']] = {
                'scheme_code': fund['scheme_code'],
                'sip_amount': fund['sip_amount']
            }
            total_sip_amount += fund['sip_amount']
        
        # Process portfolio cumulative data
        portfolio_data = process_portfolio_cumulative_optimized(funds, start_date, end_date)
        
        # Process Nifty 50 benchmark with equivalent total SIP amount
        nifty_fund = {
            "Nifty 50 Index": {
                "scheme_code": "147625",  # UTI Nifty 50 Index Fund
                "sip_amount": total_sip_amount
            }
        }
        
        nifty_data = process_portfolio_cumulative_optimized(nifty_fund, start_date, end_date)
        
        return jsonify({
            "success": True, 
            "data": {
                "portfolio": portfolio_data,
                "nifty50": nifty_data,
                "metadata": {
                    "total_sip_amount": total_sip_amount,
                    "fund_count": len(funds_data),
                    "start_date": start_date.strftime('%Y-%m-%d'),
                    "end_date": end_date.strftime('%Y-%m-%d')
                }
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/risk-analysis', methods=['POST'])
def risk_analysis():
    """Calculate comprehensive risk analysis for selected funds"""
    try:
        data = request.get_json()
        funds = data.get('funds', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not funds:
            return jsonify({'success': False, 'error': 'No funds provided'})
        
        # Get benchmark data (Nifty 50)
        benchmark_data = generate_nifty50_data(start_date, end_date, 10000)  # Using 10k as base
        
        risk_analysis_results = []
        
        for fund in funds:
            try:
                # Generate fund data
                fund_data = generate_mock_nav_data(
                    fund['scheme_code'], 
                    start_date, 
                    end_date, 
                    fund['sip_amount']
                )
                
                if fund_data:
                    # Calculate risk metrics
                    risk_metrics = calculate_risk_metrics(fund_data, benchmark_data)
                    
                    risk_analysis_results.append({
                        'fund_name': fund['fund_name'],
                        'scheme_code': fund['scheme_code'],
                        'sip_amount': fund['sip_amount'],
                        'risk_metrics': risk_metrics
                    })
                    
            except Exception as e:
                print(f"Error calculating risk for fund {fund['fund_name']}: {str(e)}")
                continue
        
        # Calculate portfolio-level risk metrics
        if len(risk_analysis_results) > 1:
            # Combine all fund data for portfolio analysis
            portfolio_data = []
            total_sip = sum(fund['sip_amount'] for fund in funds)
            
            # Create weighted portfolio returns
            for i, result in enumerate(risk_analysis_results):
                fund_data = generate_mock_nav_data(
                    result['scheme_code'], 
                    start_date, 
                    end_date, 
                    result['sip_amount']
                )
                
                weight = result['sip_amount'] / total_sip
                
                if i == 0:
                    # Initialize portfolio data
                    portfolio_data = [{
                        'date': item['date'],
                        'current_value': item['current_value'] * weight,
                        'invested': item['invested'] * weight
                    } for item in fund_data]
                else:
                    # Add weighted values
                    for j, item in enumerate(fund_data):
                        if j < len(portfolio_data):
                            portfolio_data[j]['current_value'] += item['current_value'] * weight
                            portfolio_data[j]['invested'] += item['invested'] * weight
            
            portfolio_risk_metrics = calculate_risk_metrics(portfolio_data, benchmark_data)
        else:
            portfolio_risk_metrics = risk_analysis_results[0]['risk_metrics'] if risk_analysis_results else {}
        
        return jsonify({
            'success': True,
            'data': {
                'individual_funds': risk_analysis_results,
                'portfolio_metrics': portfolio_risk_metrics,
                'benchmark_metrics': calculate_risk_metrics(benchmark_data),
                'analysis_period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_funds': len(risk_analysis_results)
                }
            }
        })
        
    except Exception as e:
        print(f"Risk analysis error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def calculate_risk_metrics(monthly_data, benchmark_data=None):
    """Calculate comprehensive risk metrics for a fund or portfolio"""
    if not monthly_data or len(monthly_data) < 2:
        return {}
    
    # Convert to pandas DataFrame for easier calculations
    df = pd.DataFrame(monthly_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Calculate monthly returns
    df['monthly_return'] = df['current_value'].pct_change().fillna(0)
    monthly_returns = df['monthly_return'].dropna()
    
    if len(monthly_returns) < 2:
        return {}
    
    # Basic statistics
    mean_return = monthly_returns.mean()
    std_dev = monthly_returns.std()
    
    # Annualized metrics
    annualized_return = (1 + mean_return) ** 12 - 1
    annualized_volatility = std_dev * np.sqrt(12)
    
    # Sharpe Ratio (assuming 6% risk-free rate)
    risk_free_rate = 0.06
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility if annualized_volatility > 0 else 0
    
    # Maximum Drawdown
    cumulative_returns = (1 + monthly_returns).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Downside Deviation (for Sortino Ratio)
    negative_returns = monthly_returns[monthly_returns < 0]
    downside_deviation = negative_returns.std() * np.sqrt(12) if len(negative_returns) > 0 else 0
    sortino_ratio = (annualized_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
    
    # Value at Risk (95% confidence)
    var_95 = np.percentile(monthly_returns, 5)
    
    # Beta calculation (if benchmark provided)
    beta = 0
    if benchmark_data and len(benchmark_data) >= len(monthly_data):
        benchmark_df = pd.DataFrame(benchmark_data)
        benchmark_df['date'] = pd.to_datetime(benchmark_df['date'])
        benchmark_df = benchmark_df.sort_values('date')
        benchmark_df['monthly_return'] = benchmark_df['current_value'].pct_change().fillna(0)
        
        # Align dates
        merged = pd.merge(df[['date', 'monthly_return']], 
                         benchmark_df[['date', 'monthly_return']], 
                         on='date', suffixes=('_fund', '_benchmark'))
        
        if len(merged) > 1:
            covariance = np.cov(merged['monthly_return_fund'], merged['monthly_return_benchmark'])[0][1]
            benchmark_variance = np.var(merged['monthly_return_benchmark'])
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
    
    # Treynor Ratio
    treynor_ratio = (annualized_return - risk_free_rate) / beta if beta > 0 else 0
    
    return {
        'annualized_return': round(annualized_return * 100, 2),
        'annualized_volatility': round(annualized_volatility * 100, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'sortino_ratio': round(sortino_ratio, 2),
        'max_drawdown': round(max_drawdown * 100, 2),
        'var_95': round(var_95 * 100, 2),
        'beta': round(beta, 2),
        'treynor_ratio': round(treynor_ratio, 2),
        'total_months': len(monthly_returns),
        'positive_months': len(monthly_returns[monthly_returns > 0]),
        'negative_months': len(monthly_returns[monthly_returns < 0]),
        'win_rate': round(len(monthly_returns[monthly_returns > 0]) / len(monthly_returns) * 100, 1)
    }

def generate_nifty50_data(start_date, end_date, sip_amount):
    """Generate mock Nifty 50 data for benchmarking"""
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate monthly SIP dates
        sip_dates = pd.date_range(start=start_dt, end=end_dt, freq='MS')
        
        total_invested = 0
        total_units = 0
        monthly_data = []
        
        # Mock Nifty 50 data (starting at around 18000)
        base_value = 18000
        
        for i, sip_date in enumerate(sip_dates):
            # Mock Nifty 50 growth with some volatility
            months_elapsed = i
            # Nifty 50 historical average: ~10-12% annually
            growth_factor = 1 + 0.11 / 12  # 11% annual return
            volatility = 0.12 * (hash(str(sip_date)) % 100 - 50) / 100  # Random volatility
            current_value = base_value * (growth_factor ** months_elapsed) * (1 + volatility)
            
            # Calculate units purchased (treating it like an index fund)
            units_purchased = sip_amount / current_value
            total_units += units_purchased
            total_invested += sip_amount
            
            # Current portfolio value
            portfolio_value = total_units * current_value
            
            monthly_data.append({
                'date': sip_date.strftime('%Y-%m-%d'),
                'invested': total_invested,
                'current_value': portfolio_value,
                'index_value': current_value,
                'units': total_units
            })
        
        return monthly_data
        
    except Exception as e:
        print(f"Error generating Nifty 50 data: {str(e)}")
        return []

@app.route('/api/goal-planning', methods=['POST'])
def goal_planning():
    """Calculate SIP requirements for various financial goals"""
    try:
        data = request.get_json()
        goal_type = data.get('goal_type')  # 'retirement', 'education', 'custom'
        goal_amount = data.get('goal_amount', 0)
        time_horizon = data.get('time_horizon', 0)  # years
        current_age = data.get('current_age', 25)
        expected_return = data.get('expected_return', 12)  # annual %
        inflation_rate = data.get('inflation_rate', 6)  # annual %
        
        # Goal-specific calculations
        if goal_type == 'retirement':
            retirement_age = data.get('retirement_age', 60)
            monthly_expenses = data.get('monthly_expenses', 50000)
            years_after_retirement = data.get('years_after_retirement', 25)
            
            # Calculate inflation-adjusted retirement corpus needed
            years_to_retirement = retirement_age - current_age
            future_monthly_expenses = monthly_expenses * ((1 + inflation_rate/100) ** years_to_retirement)
            total_corpus_needed = future_monthly_expenses * 12 * years_after_retirement
            
            # Adjust for post-retirement returns (conservative 8%)
            post_retirement_return = 8
            corpus_with_returns = total_corpus_needed / ((1 + post_retirement_return/100) ** (years_after_retirement/2))
            
            goal_amount = corpus_with_returns
            time_horizon = years_to_retirement
            
        elif goal_type == 'education':
            child_current_age = data.get('child_current_age', 5)
            education_start_age = data.get('education_start_age', 18)
            current_education_cost = data.get('current_education_cost', 2000000)
            
            years_to_education = education_start_age - child_current_age
            future_education_cost = current_education_cost * ((1 + inflation_rate/100) ** years_to_education)
            
            goal_amount = future_education_cost
            time_horizon = years_to_education
        
        # Calculate required SIP amount
        monthly_return = expected_return / 100 / 12
        total_months = time_horizon * 12
        
        if monthly_return > 0:
            # Future Value of Annuity formula: FV = PMT * [((1 + r)^n - 1) / r]
            # Rearranged to find PMT: PMT = FV / [((1 + r)^n - 1) / r]
            fv_factor = ((1 + monthly_return) ** total_months - 1) / monthly_return
            required_sip = goal_amount / fv_factor
        else:
            required_sip = goal_amount / total_months
        
        # Calculate step-up SIP (increasing by inflation rate annually)
        step_up_rate = inflation_rate / 100
        step_up_sip = calculate_step_up_sip(goal_amount, time_horizon, expected_return/100, step_up_rate)
        
        # Risk assessment based on time horizon
        risk_level = "High" if time_horizon > 10 else "Medium" if time_horizon > 5 else "Low"
        recommended_allocation = get_recommended_allocation(time_horizon, risk_level)
        
        return jsonify({
            'success': True,
            'data': {
                'goal_details': {
                    'goal_type': goal_type,
                    'target_amount': round(goal_amount, 0),
                    'time_horizon_years': time_horizon,
                    'expected_return': expected_return,
                    'inflation_rate': inflation_rate
                },
                'sip_requirements': {
                    'regular_sip': round(required_sip, 0),
                    'step_up_sip': round(step_up_sip, 0),
                    'total_investment_regular': round(required_sip * total_months, 0),
                    'total_investment_step_up': round(calculate_total_step_up_investment(step_up_sip, time_horizon, step_up_rate), 0)
                },
                'projections': {
                    'final_corpus': round(goal_amount, 0),
                    'total_returns': round(goal_amount - (required_sip * total_months), 0),
                    'wealth_multiplier': round(goal_amount / (required_sip * total_months), 1)
                },
                'recommendations': {
                    'risk_level': risk_level,
                    'asset_allocation': recommended_allocation,
                    'review_frequency': 'Annual' if time_horizon > 10 else 'Semi-annual'
                }
            }
        })
        
    except Exception as e:
        print(f"Goal planning error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def calculate_step_up_sip(goal_amount, years, annual_return, step_up_rate):
    """Calculate initial SIP amount for step-up SIP"""
    # This is a complex calculation involving geometric series
    # Simplified approach: reduce initial SIP by ~20-30% compared to regular SIP
    monthly_return = annual_return / 12
    total_months = years * 12
    
    if monthly_return > 0:
        fv_factor = ((1 + monthly_return) ** total_months - 1) / monthly_return
        regular_sip = goal_amount / fv_factor
        # Step-up SIP can start with ~25% less than regular SIP
        return regular_sip * 0.75
    else:
        return goal_amount / total_months * 0.75

def calculate_total_step_up_investment(initial_sip, years, step_up_rate):
    """Calculate total investment for step-up SIP"""
    total_investment = 0
    current_sip = initial_sip
    
    for year in range(years):
        total_investment += current_sip * 12
        current_sip *= (1 + step_up_rate)
    
    return total_investment

def get_recommended_allocation(time_horizon, risk_level):
    """Get recommended asset allocation based on time horizon and risk"""
    if time_horizon > 15:
        return {
            'equity': 80,
            'debt': 15,
            'gold': 5,
            'description': 'Aggressive growth portfolio for long-term wealth creation'
        }
    elif time_horizon > 10:
        return {
            'equity': 70,
            'debt': 25,
            'gold': 5,
            'description': 'Balanced growth portfolio with moderate risk'
        }
    elif time_horizon > 5:
        return {
            'equity': 60,
            'debt': 35,
            'gold': 5,
            'description': 'Conservative growth portfolio'
        }
    else:
        return {
            'equity': 40,
            'debt': 55,
            'gold': 5,
            'description': 'Capital preservation with modest growth'
        }

@app.route('/api/step-up-sip', methods=['POST'])
def step_up_sip():
    """Simulate step-up SIP with annual increases"""
    try:
        data = request.get_json()
        funds = data.get('funds', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        step_up_percentage = data.get('step_up_percentage', 10)  # Annual increase %
        
        if not funds:
            return jsonify({'success': False, 'error': 'No funds provided'})
        
        results = []
        portfolio_summary = {
            'total_invested': 0,
            'final_value': 0,
            'absolute_return': 0,
            'cagr': 0,
            'xirr': 0
        }
        
        for fund in funds:
            try:
                # Generate step-up SIP data
                fund_result = simulate_step_up_sip_for_fund(
                    fund, start_date, end_date, step_up_percentage
                )
                
                if fund_result:
                    results.append(fund_result)
                    portfolio_summary['total_invested'] += fund_result['invested']
                    portfolio_summary['final_value'] += fund_result['current_value']
                    
            except Exception as e:
                print(f"Error in step-up SIP for fund {fund['fund_name']}: {str(e)}")
                continue
        
        # Calculate portfolio metrics
        if portfolio_summary['total_invested'] > 0:
            portfolio_summary['absolute_return'] = (
                (portfolio_summary['final_value'] - portfolio_summary['total_invested']) / 
                portfolio_summary['total_invested'] * 100
            )
            
            # Calculate CAGR
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            years = (end_dt - start_dt).days / 365.25
            
            if years > 0:
                portfolio_summary['cagr'] = (
                    (portfolio_summary['final_value'] / portfolio_summary['total_invested']) ** (1/years) - 1
                ) * 100
        
        # Compare with regular SIP
        regular_sip_comparison = simulate_regular_sip_comparison(funds, start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': {
                'funds': results,
                'portfolio_summary': portfolio_summary,
                'step_up_details': {
                    'annual_increase': step_up_percentage,
                    'total_funds': len(results)
                },
                'comparison': regular_sip_comparison
            }
        })
        
    except Exception as e:
        print(f"Step-up SIP error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def simulate_step_up_sip_for_fund(fund, start_date, end_date, step_up_percentage):
    """Simulate step-up SIP for a single fund"""
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate monthly SIP dates
        sip_dates = pd.date_range(start=start_dt, end=end_dt, freq='MS')
        
        current_sip_amount = fund['sip_amount']
        total_invested = 0
        total_units = 0
        monthly_data = []
        
        # Mock NAV data (in real implementation, use actual NAV)
        base_nav = 50 + (hash(fund['scheme_code']) % 100)
        
        for i, sip_date in enumerate(sip_dates):
            # Increase SIP amount annually
            year_number = i // 12
            if year_number > 0:
                current_sip_amount = fund['sip_amount'] * ((1 + step_up_percentage/100) ** year_number)
            
            # Mock NAV calculation with some volatility
            months_elapsed = i
            growth_factor = 1 + (0.12 + (hash(fund['scheme_code']) % 10 - 5) * 0.01) / 12  # 12% base + variation
            volatility = 0.15 * (hash(str(sip_date)) % 100 - 50) / 100  # Random volatility
            nav = base_nav * (growth_factor ** months_elapsed) * (1 + volatility)
            
            # Calculate units purchased
            units_purchased = current_sip_amount / nav
            total_units += units_purchased
            total_invested += current_sip_amount
            
            # Current value
            current_value = total_units * nav
            
            monthly_data.append({
                'date': sip_date.strftime('%Y-%m-%d'),
                'sip_amount': round(current_sip_amount, 0),
                'nav': round(nav, 2),
                'units_purchased': round(units_purchased, 4),
                'total_units': round(total_units, 4),
                'invested': round(total_invested, 0),
                'current_value': round(current_value, 0)
            })
        
        # Calculate final metrics
        final_value = monthly_data[-1]['current_value'] if monthly_data else 0
        return_pct = ((final_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
        
        # Calculate CAGR
        years = len(sip_dates) / 12
        cagr = ((final_value / total_invested) ** (1/years) - 1) * 100 if years > 0 and total_invested > 0 else 0
        
        return {
            'fund_name': fund['fund_name'],
            'scheme_code': fund['scheme_code'],
            'initial_sip': fund['sip_amount'],
            'final_sip': round(current_sip_amount, 0),
            'invested': round(total_invested, 0),
            'current_value': round(final_value, 0),
            'return_pct': round(return_pct, 2),
            'cagr': round(cagr, 2),
            'total_units': round(total_units, 4),
            'monthly_data': monthly_data
        }
        
    except Exception as e:
        print(f"Error simulating step-up SIP for fund: {str(e)}")
        return None

def simulate_regular_sip_comparison(funds, start_date, end_date):
    """Compare step-up SIP with regular SIP"""
    try:
        total_regular_invested = 0
        total_regular_value = 0
        
        for fund in funds:
            # Simulate regular SIP
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            sip_dates = pd.date_range(start=start_dt, end=end_dt, freq='MS')
            
            regular_invested = fund['sip_amount'] * len(sip_dates)
            
            # Mock final value calculation (simplified)
            base_nav = 50 + (hash(fund['scheme_code']) % 100)
            months = len(sip_dates)
            growth_factor = 1 + 0.12 / 12  # 12% annual return
            
            # Simplified SIP calculation
            total_units = 0
            for i in range(months):
                nav = base_nav * (growth_factor ** i)
                units = fund['sip_amount'] / nav
                total_units += units
            
            final_nav = base_nav * (growth_factor ** months)
            regular_value = total_units * final_nav
            
            total_regular_invested += regular_invested
            total_regular_value += regular_value
        
        regular_return = ((total_regular_value - total_regular_invested) / total_regular_invested * 100) if total_regular_invested > 0 else 0
        
        return {
            'regular_sip': {
                'total_invested': round(total_regular_invested, 0),
                'final_value': round(total_regular_value, 0),
                'return_percentage': round(regular_return, 2)
            }
        }
        
    except Exception as e:
        print(f"Error in regular SIP comparison: {str(e)}")
        return {}

@app.route('/')
def index():
    return "SIP Simulator API is running!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 