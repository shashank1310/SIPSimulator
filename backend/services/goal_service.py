# Goal planning service for SIP Simulator
from datetime import datetime
from utils.calculations import calculate_goal_sip_requirements, get_asset_allocation_recommendation, determine_risk_level
from config import DEFAULT_EXPECTED_RETURN, DEFAULT_INFLATION_RATE

class GoalService:
    def __init__(self):
        pass
    
    def calculate_goal_requirements(self, goal_data):
        """Calculate SIP requirements for various financial goals"""
        try:
            goal_type = goal_data.get('goal_type')
            current_age = goal_data.get('current_age')
            expected_return = goal_data.get('expected_return', DEFAULT_EXPECTED_RETURN)
            inflation_rate = goal_data.get('inflation_rate', DEFAULT_INFLATION_RATE)
            
            # Calculate goal-specific parameters
            if goal_type == 'retirement':
                goal_details = self._calculate_retirement_goal(goal_data, expected_return, inflation_rate)
            elif goal_type == 'education':
                goal_details = self._calculate_education_goal(goal_data, expected_return, inflation_rate)
            elif goal_type == 'custom':
                goal_details = self._calculate_custom_goal(goal_data, expected_return, inflation_rate)
            else:
                raise Exception("Invalid goal type")
            
            # Calculate SIP requirements
            sip_requirements = calculate_goal_sip_requirements(
                goal_details['target_amount'],
                goal_details['time_horizon_years'],
                expected_return,
                inflation_rate
            )
            
            # Calculate projections
            projections = self._calculate_projections(goal_details, sip_requirements)
            
            # Get recommendations
            recommendations = self._get_recommendations(goal_details)
            
            return {
                'goal_details': goal_details,
                'sip_requirements': sip_requirements,
                'projections': projections,
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"Goal calculation error: {e}")
            raise e
    
    def _calculate_retirement_goal(self, goal_data, expected_return, inflation_rate):
        """Calculate retirement goal parameters"""
        current_age = goal_data.get('current_age')
        retirement_age = goal_data.get('retirement_age', 60)
        monthly_expenses = goal_data.get('monthly_expenses', 50000)
        years_after_retirement = goal_data.get('years_after_retirement', 25)
        
        time_horizon = retirement_age - current_age
        
        # Calculate inflation-adjusted monthly expenses at retirement
        future_monthly_expenses = monthly_expenses * ((1 + inflation_rate/100) ** time_horizon)
        
        # Calculate total corpus needed (25x annual expenses rule)
        annual_expenses_at_retirement = future_monthly_expenses * 12
        target_amount = annual_expenses_at_retirement * years_after_retirement
        
        return {
            'goal_type': 'Retirement Planning',
            'target_amount': int(target_amount),
            'time_horizon_years': time_horizon,
            'expected_return': expected_return,
            'current_monthly_expenses': monthly_expenses,
            'future_monthly_expenses': int(future_monthly_expenses)
        }
    
    def _calculate_education_goal(self, goal_data, expected_return, inflation_rate):
        """Calculate education goal parameters"""
        child_current_age = goal_data.get('child_current_age', 5)
        education_start_age = goal_data.get('education_start_age', 18)
        current_education_cost = goal_data.get('current_education_cost', 1000000)
        
        time_horizon = education_start_age - child_current_age
        
        # Calculate inflation-adjusted education cost
        future_education_cost = current_education_cost * ((1 + inflation_rate/100) ** time_horizon)
        
        return {
            'goal_type': 'Child Education',
            'target_amount': int(future_education_cost),
            'time_horizon_years': time_horizon,
            'expected_return': expected_return,
            'current_cost': current_education_cost,
            'future_cost': int(future_education_cost)
        }
    
    def _calculate_custom_goal(self, goal_data, expected_return, inflation_rate):
        """Calculate custom goal parameters"""
        goal_amount = goal_data.get('goal_amount')
        time_horizon = goal_data.get('time_horizon')
        
        # Adjust for inflation
        inflation_adjusted_amount = goal_amount * ((1 + inflation_rate/100) ** time_horizon)
        
        return {
            'goal_type': 'Custom Goal',
            'target_amount': int(inflation_adjusted_amount),
            'time_horizon_years': time_horizon,
            'expected_return': expected_return,
            'nominal_amount': goal_amount,
            'inflation_adjusted_amount': int(inflation_adjusted_amount)
        }
    
    def _calculate_projections(self, goal_details, sip_requirements):
        """Calculate investment projections"""
        target_amount = goal_details['target_amount']
        total_investment = sip_requirements['total_investment_regular']
        
        total_returns = target_amount - total_investment
        wealth_multiplier = sip_requirements['wealth_multiplier']
        
        return {
            'total_returns': int(total_returns),
            'wealth_multiplier': wealth_multiplier,
            'return_percentage': round((total_returns / total_investment) * 100, 1)
        }
    
    def _get_recommendations(self, goal_details):
        """Get investment recommendations based on goal"""
        time_horizon = goal_details['time_horizon_years']
        target_amount = goal_details['target_amount']
        
        # Determine risk level
        risk_level = determine_risk_level(time_horizon, target_amount)
        
        # Get asset allocation
        risk_tolerance = 'aggressive' if risk_level == 'High' else 'moderate' if risk_level == 'Medium' else 'conservative'
        asset_allocation = get_asset_allocation_recommendation(time_horizon, risk_tolerance)
        
        return {
            'risk_level': risk_level,
            'asset_allocation': asset_allocation,
            'investment_strategy': self._get_investment_strategy(time_horizon, risk_level)
        }
    
    def _get_investment_strategy(self, time_horizon, risk_level):
        """Get investment strategy recommendations"""
        if time_horizon >= 15:
            return "Long-term wealth creation with high equity allocation"
        elif time_horizon >= 10:
            return "Balanced approach with moderate equity exposure"
        elif time_horizon >= 5:
            return "Conservative strategy with capital preservation focus"
        else:
            return "Short-term strategy with debt-heavy allocation" 