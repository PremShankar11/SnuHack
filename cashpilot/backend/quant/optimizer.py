"""
Linear Programming Optimization Engine
Minimizes late fees + goodwill penalties while respecting constraints
"""
import numpy as np
from scipy.optimize import linprog
from typing import Dict, List, Any
from datetime import datetime


def optimize_payments(
    balance: float,
    obligations: List[Dict[str, Any]],
    entities: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Optimize payment decisions using linear programming.
    
    Objective: Minimize total_damage = late_fees + goodwill_penalties
    
    Constraints:
    - Sum of payments <= balance
    - Tier 0 obligations must be fully paid
    - Other obligations can be fractional (0 to 1)
    
    Args:
        balance: Current cash balance
        obligations: List of pending obligations
        entities: Dict mapping entity_id to entity data
    
    Returns:
        {
            "optimization_result": [
                {
                    "obligation_id": str,
                    "entity_name": str,
                    "math_decision": "FULL" | "FRACTIONAL_PAYMENT" | "DELAY",
                    "pay_now_amount": float,
                    "delay_amount": float,
                    "requested_extension_days": int
                }
            ]
        }
    """
    if not obligations:
        return {"optimization_result": []}
    
    n = len(obligations)
    
    # Build cost vector (coefficients for objective function)
    # cost[i] = late_fee_cost + goodwill_penalty for NOT paying obligation i
    costs = []
    ob_data = []
    
    for ob in obligations:
        entity_id = str(ob['entity_id'])
        entity = entities.get(entity_id, {})
        
        amount = abs(float(ob['amount']))
        late_fee_rate = float(entity.get('late_fee_rate', 0.0))
        goodwill_score = float(entity.get('goodwill_score', 100))
        
        # Cost of NOT paying (delaying)
        late_fee_cost = amount * late_fee_rate
        goodwill_penalty = amount * ((100 - goodwill_score) / 100.0)
        total_cost = late_fee_cost + goodwill_penalty
        
        costs.append(total_cost)
        ob_data.append({
            'obligation': ob,
            'entity': entity,
            'amount': amount
        })
    
    # Decision variables: x[i] = fraction to delay (0 = pay full, 1 = delay full)
    # We want to MINIMIZE the cost of delays, so we minimize sum(cost[i] * x[i])
    c = np.array(costs)
    
    # Constraint: sum of payments <= balance
    # payment[i] = amount[i] * (1 - x[i])
    # sum(amount[i] * (1 - x[i])) <= balance
    # sum(amount[i]) - sum(amount[i] * x[i]) <= balance
    # -sum(amount[i] * x[i]) <= balance - sum(amount[i])
    # sum(amount[i] * x[i]) >= sum(amount[i]) - balance
    
    amounts = np.array([d['amount'] for d in ob_data])
    total_obligations = np.sum(amounts)
    
    # A_ub * x <= b_ub
    # We need: sum(amount[i] * x[i]) >= total_obligations - balance
    # Rewrite as: -sum(amount[i] * x[i]) <= -(total_obligations - balance)
    A_ub = [-amounts]
    b_ub = [-(total_obligations - balance)]
    
    # Bounds: 0 <= x[i] <= 1 for all i
    # Exception: Tier 0 must be paid (x[i] = 0)
    bounds = []
    for d in ob_data:
        entity = d['entity']
        if entity.get('ontology_tier') == 0:
            # Must pay (cannot delay)
            bounds.append((0, 0))
        else:
            # Can delay partially or fully
            bounds.append((0, 1))
    
    # Solve
    try:
        result = linprog(
            c=c,
            A_ub=A_ub,
            b_ub=b_ub,
            bounds=bounds,
            method='highs'
        )
        
        if not result.success:
            # Fallback: pay as much as possible in order
            x = np.ones(n)
            remaining = balance
            for i in range(n):
                if ob_data[i]['entity'].get('ontology_tier') == 0:
                    x[i] = 0  # Must pay
                    remaining -= ob_data[i]['amount']
                elif remaining >= ob_data[i]['amount']:
                    x[i] = 0  # Pay full
                    remaining -= ob_data[i]['amount']
                else:
                    # Partial payment
                    if remaining > 0:
                        fraction_paid = remaining / ob_data[i]['amount']
                        x[i] = 1 - fraction_paid
                        remaining = 0
                    else:
                        x[i] = 1  # Delay full
        else:
            x = result.x
    except Exception:
        # Fallback to simple heuristic
        x = np.ones(n)
        remaining = balance
        for i in range(n):
            if ob_data[i]['entity'].get('ontology_tier') == 0:
                x[i] = 0
                remaining -= ob_data[i]['amount']
            elif remaining >= ob_data[i]['amount']:
                x[i] = 0
                remaining -= ob_data[i]['amount']
            else:
                if remaining > 0:
                    x[i] = 1 - (remaining / ob_data[i]['amount'])
                    remaining = 0
                else:
                    x[i] = 1
    
    # Build result
    optimization_result = []
    
    for i, d in enumerate(ob_data):
        ob = d['obligation']
        entity = d['entity']
        amount = d['amount']
        delay_fraction = x[i]
        
        pay_now_amount = amount * (1 - delay_fraction)
        delay_amount = amount * delay_fraction
        
        # Determine decision type
        if delay_fraction < 0.01:
            math_decision = "FULL"
            requested_extension_days = 0
        elif delay_fraction > 0.99:
            math_decision = "DELAY"
            requested_extension_days = 7  # Default extension request
        else:
            math_decision = "FRACTIONAL_PAYMENT"
            requested_extension_days = 7
        
        optimization_result.append({
            "obligation_id": str(ob['id']),
            "entity_name": entity.get('name', 'Unknown'),
            "math_decision": math_decision,
            "pay_now_amount": round(pay_now_amount, 2),
            "delay_amount": round(delay_amount, 2),
            "requested_extension_days": requested_extension_days
        })
    
    return {
        "optimization_result": optimization_result
    }
