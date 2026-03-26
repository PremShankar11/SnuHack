"""
Runway Engine - Deterministic "Days to Zero" (D2Z) calculation.

Algorithm: Day-by-day ledger simulation over a 30-day horizon.
Input:  Current balance + pending obligations
Output: Days until balance hits $0, breach date, daily projection

ZERO AI/LLM - Pure math only.
"""

from datetime import timedelta
from typing import Dict
from core.db import get_db_connection


def calculate_runway(company_id: str) -> Dict:
    """
    Calculates the deterministic Days to Zero (D2Z) metric.

    Returns:
        {
            "days_to_zero": int,
            "breach_date": str (ISO format) or None,
            "daily_projection": List[Dict] - 30 day balance forecast,
            "current_balance": float
        }
    """
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("Database connection failed")

    cur = conn.cursor()

    try:
        # Get current state
        cur.execute(
            "SELECT plaid_current_balance, current_simulated_date FROM companies WHERE id = %s;",
            (company_id,)
        )
        company = cur.fetchone()
        if not company:
            raise ValueError("Company not found")

        current_balance = float(company['plaid_current_balance'])
        simulated_now = company['current_simulated_date']

        # Get all pending obligations for next 30 days
        horizon = simulated_now + timedelta(days=30)
        cur.execute(
            "SELECT amount, due_date FROM obligations "
            "WHERE status = 'PENDING' AND due_date > %s AND due_date <= %s "
            "ORDER BY due_date;",
            (simulated_now, horizon)
        )
        obligations = cur.fetchall()

        # Build daily projection
        daily_projection = []
        running_balance = current_balance
        breach_date = None
        days_to_zero = 30  # Default if no breach

        for i in range(30):
            day = simulated_now + timedelta(days=i)

            # Sum all obligations due on this day
            day_net = sum(
                float(ob['amount'])
                for ob in obligations
                if ob['due_date'] == day
            )

            running_balance += day_net

            daily_projection.append({
                "date": day.isoformat(),
                "balance": round(running_balance, 2),
                "day_net": round(day_net, 2)
            })

            # Detect first breach
            if running_balance < 0 and breach_date is None:
                breach_date = day.isoformat()
                days_to_zero = i

        return {
            "days_to_zero": days_to_zero,
            "breach_date": breach_date,
            "daily_projection": daily_projection,
            "current_balance": current_balance
        }

    finally:
        cur.close()
        conn.close()
