"""
Monte Carlo Simulation Engine
Probabilistic runway analysis with payment delay uncertainty
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any


def monte_carlo_simulation(
    balance: float,
    obligations: List[Dict[str, Any]],
    entities: Dict[str, Dict[str, Any]],
    simulations: int = 1000
) -> Dict[str, float]:
    """
    Run Monte Carlo simulation to estimate survival probability.
    
    Args:
        balance: Current cash balance
        obligations: List of pending obligations
        entities: Dict mapping entity_id to entity data (with avg_latency_days)
        simulations: Number of simulation runs
    
    Returns:
        {
            "survival_probability": float (0.0 to 1.0)
        }
    """
    if not obligations:
        return {"survival_probability": 1.0}
    
    survival_count = 0
    
    for _ in range(simulations):
        sim_balance = balance
        sim_obligations = []
        
        # Apply random delays to each obligation
        for ob in obligations:
            entity_id = str(ob['entity_id'])
            entity = entities.get(entity_id, {})
            avg_latency = entity.get('avg_latency_days', 0)
            
            # Sample delay from normal distribution N(0, avg_latency_days)
            delay_days = int(np.random.normal(0, max(avg_latency, 1)))
            delay_days = max(0, delay_days)  # No negative delays
            
            due_date = ob['due_date']
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date).date()
            
            adjusted_due = due_date + timedelta(days=delay_days)
            
            sim_obligations.append({
                'amount': float(ob['amount']),
                'due_date': adjusted_due
            })
        
        # Sort by adjusted due date
        sim_obligations.sort(key=lambda x: x['due_date'])
        
        # Simulate balance trajectory
        survived = True
        for ob in sim_obligations:
            sim_balance += ob['amount']
            if sim_balance < 0:
                survived = False
                break
        
        if survived:
            survival_count += 1
    
    survival_probability = survival_count / simulations
    
    return {
        "survival_probability": round(survival_probability, 4)
    }
