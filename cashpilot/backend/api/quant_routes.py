"""
Quant Engine API Routes
Exposes deterministic financial calculation endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Any

from core.db import get_db_connection
from quant.runway import calculate_runway
from quant.phantom_balance import calculate_usable_cash
from quant.monte_carlo import monte_carlo_simulation
from quant.optimizer import optimize_payments


router = APIRouter()


def fetch_financial_data() -> Dict[str, Any]:
    """
    Fetch all required data from Supabase for quant calculations.
    
    Returns:
        {
            "balance": float,
            "obligations": List[Dict],
            "entities": Dict[entity_id -> entity_data]
        }
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cur = conn.cursor()
    try:
        # Get company balance
        cur.execute("SELECT plaid_current_balance FROM companies LIMIT 1;")
        company = cur.fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        balance = float(company['plaid_current_balance'])
        
        # Get pending obligations
        cur.execute(
            "SELECT id, entity_id, amount, due_date, is_locked "
            "FROM obligations WHERE status = 'PENDING' ORDER BY due_date;"
        )
        obligations_raw = cur.fetchall()
        
        obligations = []
        for ob in obligations_raw:
            obligations.append({
                'id': ob['id'],
                'entity_id': ob['entity_id'],
                'amount': float(ob['amount']),
                'due_date': ob['due_date'],
                'is_locked': ob['is_locked']
            })
        
        # Get entities with O(1) lookup
        cur.execute(
            "SELECT id, name, entity_type, ontology_tier, goodwill_score, "
            "late_fee_rate, avg_latency_days FROM entities;"
        )
        entities_raw = cur.fetchall()
        
        entities = {}
        for ent in entities_raw:
            entities[str(ent['id'])] = {
                'id': ent['id'],
                'name': ent['name'],
                'entity_type': ent['entity_type'],
                'ontology_tier': int(ent['ontology_tier']),
                'goodwill_score': int(ent['goodwill_score']) if ent['goodwill_score'] else 100,
                'late_fee_rate': float(ent['late_fee_rate']) if ent['late_fee_rate'] else 0.0,
                'avg_latency_days': int(ent['avg_latency_days']) if ent['avg_latency_days'] else 0
            }
        
        return {
            "balance": balance,
            "obligations": obligations,
            "entities": entities
        }
    finally:
        cur.close()
        conn.close()


@router.get("/api/dashboard")
def get_dashboard():
    """
    GET /api/dashboard
    
    Returns global financial state with runway metrics.
    Follows shared_contracts.json global_state schema.
    
    Response:
        {
            "global_state": {
                "simulated_as_of": str,
                "plaid_balance": float,
                "phantom_usable_cash": float,
                "locked_tier_0_funds": float,
                "runway_metrics": {
                    "days_to_zero": int,
                    "liquidity_breach_date": str | null,
                    "monte_carlo_survival_prob": float
                },
                "cashflow_projection_array": [...]
            }
        }
    """
    try:
        data = fetch_financial_data()
        
        balance = data['balance']
        obligations = data['obligations']
        entities = data['entities']
        
        # Get simulated date from database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT current_simulated_date FROM companies LIMIT 1;")
        company = cur.fetchone()
        simulated_as_of = company['current_simulated_date'].isoformat() if company and company['current_simulated_date'] else datetime.now().date().isoformat()
        cur.close()
        conn.close()
        
        # Calculate phantom balance
        phantom_result = calculate_usable_cash(balance, obligations, entities)
        
        # Calculate runway
        runway_result = calculate_runway(balance, obligations)
        
        # Run Monte Carlo simulation
        mc_result = monte_carlo_simulation(balance, obligations, entities, simulations=1000)
        
        # Build cashflow projection array (14 days)
        cashflow_projection = []
        current_balance = phantom_result['usable_cash']
        
        # Parse simulated_as_of to date object
        if isinstance(simulated_as_of, str):
            base_date = datetime.fromisoformat(simulated_as_of).date()
        else:
            base_date = simulated_as_of
        
        for i in range(14):
            projection_date = base_date + timedelta(days=i)
            # Calculate net obligations for this day
            day_obligations = sum(
                float(ob['amount']) for ob in obligations
                if (ob['due_date'] if not isinstance(ob['due_date'], str) else datetime.fromisoformat(ob['due_date']).date()) == projection_date
            )
            current_balance += day_obligations
            
            cashflow_projection.append({
                "date": projection_date.isoformat(),
                "balance": round(current_balance, 2)
            })
        
        return {
            "global_state": {
                "simulated_as_of": simulated_as_of,
                "plaid_balance": balance,
                "phantom_usable_cash": phantom_result['usable_cash'],
                "locked_tier_0_funds": phantom_result['locked_amount'],
                "runway_metrics": {
                    "days_to_zero": runway_result['days_to_zero'],
                    "liquidity_breach_date": runway_result['breach_date'],
                    "monte_carlo_survival_prob": mc_result['survival_probability']
                },
                "cashflow_projection_array": cashflow_projection
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating dashboard: {str(e)}")


@router.get("/api/decision")
def get_decision():
    """
    GET /api/decision
    
    Returns optimization directive for payment decisions.
    Follows shared_contracts.json solver_directive schema.
    
    Response:
        {
            "solver_directive": {
                "breach_amount": float,
                "optimization_result": [
                    {
                        "obligation_id": str,
                        "entity_name": str,
                        "original_due": str,
                        "math_decision": "FULL" | "FRACTIONAL_PAYMENT" | "DELAY",
                        "pay_now_amount": float,
                        "delay_amount": float,
                        "requested_extension_days": int
                    }
                ]
            }
        }
    """
    try:
        data = fetch_financial_data()
        
        balance = data['balance']
        obligations = data['obligations']
        entities = data['entities']
        
        # Calculate runway to determine breach
        runway_result = calculate_runway(balance, obligations)
        
        # Calculate breach amount (if any)
        breach_amount = 0.0
        if runway_result['breach_date']:
            # Sum obligations up to breach date
            breach_date = datetime.fromisoformat(runway_result['breach_date']).date()
            total_due = sum(
                float(ob['amount']) for ob in obligations
                if ob['due_date'] <= breach_date
            )
            breach_amount = balance + total_due  # Will be negative if breach
        
        # Run optimizer
        optimizer_result = optimize_payments(balance, obligations, entities)
        
        # Add original_due dates to results
        for decision in optimizer_result['optimization_result']:
            ob_id = decision['obligation_id']
            matching_ob = next((ob for ob in obligations if str(ob['id']) == ob_id), None)
            if matching_ob:
                due_date = matching_ob['due_date']
                decision['original_due'] = due_date.isoformat() if hasattr(due_date, 'isoformat') else str(due_date)
            else:
                decision['original_due'] = None
        
        return {
            "solver_directive": {
                "breach_amount": breach_amount,
                "optimization_result": optimizer_result['optimization_result']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating decision: {str(e)}")
