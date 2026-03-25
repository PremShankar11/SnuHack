"""
Phantom Balance Engine - Virtual Liability Ring-Fencing
Calculates usable cash after locking Tier 0 obligations
"""
from typing import Dict, List, Any


def calculate_usable_cash(
    balance: float,
    obligations: List[Dict[str, Any]],
    entities: Dict[str, Dict[str, Any]]
) -> Dict[str, float]:
    """
    Calculate usable cash after ring-fencing Tier 0 obligations.
    
    Args:
        balance: Current cash balance
        obligations: List of pending obligations
        entities: Dict mapping entity_id to entity data (with ontology_tier)
    
    Returns:
        {
            "usable_cash": float,
            "locked_amount": float
        }
    """
    locked_amount = 0.0
    
    for ob in obligations:
        entity_id = str(ob['entity_id'])
        entity = entities.get(entity_id, {})
        
        # Check if Tier 0 (critical: taxes, payroll)
        if entity.get('ontology_tier') == 0:
            # Lock this obligation amount (negative for payables)
            locked_amount += abs(float(ob['amount']))
    
    usable_cash = balance - locked_amount
    
    return {
        "usable_cash": usable_cash,
        "locked_amount": locked_amount
    }
