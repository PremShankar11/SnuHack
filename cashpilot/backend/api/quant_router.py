"""
Quant Router - Unified API endpoints for Stream 2 mathematical engine.

Endpoints:
  GET /api/quant/runway      - Days to Zero calculation
  GET /api/quant/phantom      - Phantom Usable Cash
  GET /api/quant/optimize     - LP payment optimization
  GET /api/quant/monte-carlo  - Monte Carlo survival probability
"""

from fastapi import APIRouter, HTTPException
from quant.runway_engine import calculate_runway
from quant.phantom_balance import calculate_phantom_balance
from quant.optimizer import optimize_payment_strategy
from quant.monte_carlo import run_monte_carlo_simulation

router = APIRouter()


def _get_first_company_id() -> str:
    """Helper: fetch the first company ID from the database."""
    from core.db import get_db_connection
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM companies LIMIT 1;")
        company = cur.fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return str(company['id'])
    finally:
        cur.close()
        conn.close()


@router.get("/api/quant/runway")
def get_runway():
    """Calculate Days to Zero and daily projection."""
    try:
        company_id = _get_first_company_id()
        return calculate_runway(company_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/quant/phantom")
def get_phantom():
    """Calculate Phantom Usable Cash."""
    try:
        company_id = _get_first_company_id()
        return calculate_phantom_balance(company_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/quant/optimize")
def get_optimization():
    """Run Linear Programming optimization for payment strategy."""
    try:
        company_id = _get_first_company_id()
        return optimize_payment_strategy(company_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/quant/monte-carlo")
def get_monte_carlo():
    """Run Monte Carlo simulation for survival probability."""
    try:
        company_id = _get_first_company_id()
        return run_monte_carlo_simulation(company_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
