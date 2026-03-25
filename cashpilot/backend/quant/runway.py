"""
Runway Engine - Deterministic cash runway calculation
Simulates daily balance trajectory to detect liquidity breach
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any


def calculate_runway(balance: float, obligations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate days until balance reaches zero (runway).
    
    Args:
        balance: Current cash balance
        obligations: List of obligation dicts with 'amount' and 'due_date'
    
    Returns:
        {
            "days_to_zero": int,
            "breach_date": "YYYY-MM-DD" or None
        }
    """
    if not obligations:
        return {
            "days_to_zero": 999,
            "breach_date": None
        }
    
    # Sort obligations by due_date
    sorted_obs = sorted(obligations, key=lambda x: x['due_date'] if not isinstance(x['due_date'], str) else datetime.fromisoformat(x['due_date']).date())
    
    # Simulate daily balance
    current_balance = balance
    current_date = datetime.now().date()
    
    for ob in sorted_obs:
        due_date = ob['due_date']
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date).date()
        
        amount = float(ob['amount'])
        
        # Apply the obligation
        current_balance += amount
        
        # Check for breach
        if current_balance < 0:
            days_to_zero = (due_date - current_date).days
            return {
                "days_to_zero": max(0, days_to_zero),
                "breach_date": due_date.isoformat()
            }
    
    # No breach detected
    return {
        "days_to_zero": 999,
        "breach_date": None
    }
