#!/usr/bin/env python3
"""
Real-time Mutual Fund Data Sources
Alternative implementations to replace hardcoded fund data
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data source configuration
FUND_DATA_SOURCES = {
    'mfapi': {
        'name': 'MF API',
        'description': 'Free Indian Mutual Fund API',
        'website': 'https://www.mfapi.in/',
        'requires_key': False,
        'coverage': 'High',
        'speed': 'Medium',
        'reliability': 'High'
    },
    'amfi': {
        'name': 'AMFI',
        'description': 'Association of Mutual Funds in India',
        'website': 'https://www.amfiindia.com/',
        'requires_key': False,
        'coverage': 'Complete',
        'speed': 'Slow',
        'reliability': 'Very High'
    },
    'rapidapi': {
        'name': 'RapidAPI',
        'description': 'Premium mutual fund data service',
        'website': 'https://rapidapi.com/',
        'requires_key': True,
        'coverage': 'High',
        'speed': 'Fast',
        'reliability': 'High'
    },
    'hybrid': {
        'name': 'Hybrid',
        'description': 'Combines multiple sources for best coverage',
        'website': 'N/A',
        'requires_key': False,
        'coverage': 'Complete',
        'speed': 'Fast',
        'reliability': 'Very High'
    }
}

class MutualFundDataProvider:
    """Base class for mutual fund data providers"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache
        
    def search_funds(self, query, limit=50):
        """Search for mutual funds by name/AMC"""
        raise NotImplementedError
        
    def get_fund_details(self, scheme_code):
        """Get detailed fund information"""
        raise NotImplementedError
        
    def get_nav_data(self, scheme_code, start_date=None, end_date=None):
        """Get NAV data for a fund"""
        raise NotImplementedError

class MFAPIProvider(MutualFundDataProvider):
    """
    Provider using MF API (Free Indian Mutual Fund API)
    Website: https://www.mfapi.in/
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.mfapi.in"
        
    def search_funds(self, query, limit=50):
        """Search funds using MF API"""
        try:
            # Get all funds list
            cache_key = "all_funds"
            if cache_key in self.cache:
                cached_time, funds_list = self.cache[cache_key]
                if time.time() - cached_time < self.cache_duration:
                    return self._filter_funds(funds_list, query, limit)
            
            # Fetch fresh data
            response = requests.get(f"{self.base_url}/mf", timeout=10)
            if response.status_code == 200:
                funds_list = response.json()
                self.cache[cache_key] = (time.time(), funds_list)
                return self._filter_funds(funds_list, query, limit)
            else:
                logger.error(f"MF API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error in MFAPIProvider.search_funds: {e}")
            return []
    
    def _filter_funds(self, funds_list, query, limit):
        """Filter funds based on search query"""
        query_lower = query.lower()
        filtered_funds = []
        
        for fund in funds_list:
            if 'schemeName' in fund and 'schemeCode' in fund:
                fund_name = fund['schemeName'].lower()
                if (query_lower in fund_name or 
                    any(word in fund_name for word in query_lower.split())):
                    filtered_funds.append({
                        'scheme_code': str(fund['schemeCode']),
                        'fund_name': fund['schemeName'],
                        'fund_house': fund.get('fundHouse', 'Unknown')
                    })
                    
                    if len(filtered_funds) >= limit:
                        break
        
        return filtered_funds
    
    def get_fund_details(self, scheme_code):
        """Get fund details from MF API"""
        try:
            response = requests.get(f"{self.base_url}/mf/{scheme_code}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'scheme_code': scheme_code,
                    'fund_name': data.get('meta', {}).get('scheme_name', ''),
                    'fund_house': data.get('meta', {}).get('fund_house', ''),
                    'scheme_type': data.get('meta', {}).get('scheme_type', ''),
                    'scheme_category': data.get('meta', {}).get('scheme_category', ''),
                    'scheme_start_date': data.get('meta', {}).get('scheme_start_date', ''),
                    'nav': data.get('data', [{}])[0].get('nav', 0) if data.get('data') else 0,
                    'date': data.get('data', [{}])[0].get('date', '') if data.get('data') else ''
                }
            return None
        except Exception as e:
            logger.error(f"Error getting fund details for {scheme_code}: {e}")
            return None
    
    def get_nav_data(self, scheme_code, start_date=None, end_date=None):
        """Get NAV data from MF API"""
        try:
            response = requests.get(f"{self.base_url}/mf/{scheme_code}", timeout=15)
            if response.status_code == 200:
                data = response.json()
                nav_data = data.get('data', [])
                
                # Convert to DataFrame
                df = pd.DataFrame(nav_data)
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
                    df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
                    df = df.dropna().sort_values('date')
                    
                    # Filter by date range if provided
                    if start_date:
                        start_date = pd.to_datetime(start_date)
                        df = df[df['date'] >= start_date]
                    if end_date:
                        end_date = pd.to_datetime(end_date)
                        df = df[df['date'] <= end_date]
                    
                    return df
                
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error getting NAV data for {scheme_code}: {e}")
            return pd.DataFrame()

class RapidAPIProvider(MutualFundDataProvider):
    """
    Provider using RapidAPI Mutual Fund services
    Requires API key but provides more comprehensive data
    """
    
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://latest-mutual-fund-nav.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "latest-mutual-fund-nav.p.rapidapi.com"
        }
    
    def search_funds(self, query, limit=50):
        """Search funds using RapidAPI"""
        try:
            # This would depend on the specific RapidAPI endpoint structure
            # Implementation would vary based on the chosen RapidAPI service
            pass
        except Exception as e:
            logger.error(f"Error in RapidAPIProvider.search_funds: {e}")
            return []

class AMFIDataProvider(MutualFundDataProvider):
    """
    Provider using AMFI (Association of Mutual Funds in India) data
    Free but requires parsing of NAV files
    """
    
    def __init__(self):
        super().__init__()
        self.nav_url = "https://www.amfiindia.com/spages/NAVAll.txt"
        
    def search_funds(self, query, limit=50):
        """Search funds using AMFI data"""
        try:
            # Download and parse AMFI NAV file
            response = requests.get(self.nav_url, timeout=15)
            if response.status_code == 200:
                return self._parse_amfi_data(response.text, query, limit)
            return []
        except Exception as e:
            logger.error(f"Error in AMFIDataProvider.search_funds: {e}")
            return []
    
    def _parse_amfi_data(self, nav_text, query, limit):
        """Parse AMFI NAV text file"""
        funds = []
        query_lower = query.lower()
        
        lines = nav_text.strip().split('\n')
        current_amc = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # AMC name lines (no semicolon)
            if ';' not in line and line and not line.isdigit():
                current_amc = line
                continue
            
            # Fund data lines
            parts = line.split(';')
            if len(parts) >= 6:
                scheme_code = parts[0].strip()
                fund_name = parts[3].strip()
                nav = parts[4].strip()
                date = parts[5].strip()
                
                if (query_lower in fund_name.lower() and 
                    scheme_code.isdigit() and 
                    nav.replace('.', '').isdigit()):
                    
                    funds.append({
                        'scheme_code': scheme_code,
                        'fund_name': fund_name,
                        'fund_house': current_amc,
                        'nav': float(nav),
                        'date': date
                    })
                    
                    if len(funds) >= limit:
                        break
        
        return funds

class HybridDataProvider(MutualFundDataProvider):
    """
    Hybrid provider that tries multiple sources for best coverage
    Falls back to hardcoded data if all APIs fail
    """
    
    def __init__(self, rapidapi_key=None):
        super().__init__()
        self.providers = [
            MFAPIProvider(),
            AMFIDataProvider()
        ]
        
        if rapidapi_key:
            self.providers.append(RapidAPIProvider(rapidapi_key))
    
    def search_funds(self, query, limit=50):
        """Try multiple providers for fund search"""
        for provider in self.providers:
            try:
                results = provider.search_funds(query, limit)
                if results:
                    logger.info(f"Successfully got {len(results)} results from {provider.__class__.__name__}")
                    return results
            except Exception as e:
                logger.warning(f"Provider {provider.__class__.__name__} failed: {e}")
                continue
        
        # Fallback to hardcoded data
        logger.warning("All providers failed, falling back to hardcoded data")
        return self._fallback_search(query, limit)
    
    def get_nav_data(self, scheme_code, start_date=None, end_date=None):
        """Try multiple providers for NAV data"""
        for provider in self.providers:
            try:
                data = provider.get_nav_data(scheme_code, start_date, end_date)
                if not data.empty:
                    logger.info(f"Successfully got NAV data from {provider.__class__.__name__}")
                    return data
            except Exception as e:
                logger.warning(f"Provider {provider.__class__.__name__} failed for NAV data: {e}")
                continue
        
        # Fallback to mock data
        logger.warning("All providers failed for NAV data, generating mock data")
        return self._generate_fallback_nav_data(scheme_code, start_date, end_date)
    
    def _fallback_search(self, query, limit):
        """Fallback to hardcoded fund list"""
        # Import the existing hardcoded list
        from app import COMPREHENSIVE_FUND_LIST
        
        query_lower = query.lower()
        filtered_funds = []
        
        for fund in COMPREHENSIVE_FUND_LIST:
            if query_lower in fund['fund_name'].lower():
                filtered_funds.append(fund)
                if len(filtered_funds) >= limit:
                    break
        
        return filtered_funds
    
    def _generate_fallback_nav_data(self, scheme_code, start_date, end_date):
        """Generate mock NAV data as fallback"""
        # Use existing mock data generation logic
        from app import generate_optimized_mock_nav_data
        
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()
            
        return generate_optimized_mock_nav_data(scheme_code, start_date, end_date)

# Factory function to create the appropriate provider
def create_fund_data_provider(provider_type="hybrid", **kwargs):
    """Factory function to create fund data provider"""
    
    if provider_type == "mfapi":
        return MFAPIProvider()
    elif provider_type == "rapidapi":
        api_key = kwargs.get('rapidapi_key')
        if not api_key:
            raise ValueError("RapidAPI key required for RapidAPI provider")
        return RapidAPIProvider(api_key)
    elif provider_type == "amfi":
        return AMFIDataProvider()
    elif provider_type == "hybrid":
        return HybridDataProvider(kwargs.get('rapidapi_key'))
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")

# Example usage and testing
if __name__ == "__main__":
    # Test the providers
    provider = create_fund_data_provider("hybrid")
    
    # Test search
    print("Testing fund search...")
    results = provider.search_funds("HDFC", limit=10)
    for fund in results[:5]:
        print(f"- {fund['fund_name']} ({fund['scheme_code']})")
    
    # Test NAV data
    if results:
        print(f"\nTesting NAV data for {results[0]['scheme_code']}...")
        nav_data = provider.get_nav_data(results[0]['scheme_code'])
        print(f"Got {len(nav_data)} NAV records")
        if not nav_data.empty:
            print(nav_data.tail()) 