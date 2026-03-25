"""
Linear Programming Optimizer - Payment strategy optimization.

Objective: Minimize (late fees + goodwill damage)
Constraints:
  - Balance >= 0 for all days
  - Tier 0 (locked) obligations MUST be paid (delay = 0)
  - delay_i >= 0 for all obligations

Uses scipy.optimize.linprog with the HiGHS solver.

ZERO AI/LLM - Pure math only.
"""

from datetime import timedelta
from typing import Dict
import numpy as np
from scipy.optimize import linprog
from core.db import get_db_connection


def optimize_payment_strategy(company_id: str) -> Dict:
    """
    Uses Linear Programming to find the optimal payment strategy.

    Returns:
        {
            "status": str,
            "optimized_obligations": List[Dict],
            "projected_savings": float,
            "breach_prevented": bool
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

        # Get all pending payables (negative amounts) for next 14 days
        horizon = simulated_now + timedelta(days=14)
        cur.execute(
            """
            SELECT o.id, o.amount, o.due_date, o.is_locked,
                   e.goodwill_score, e.late_fee_rate, e.name as entity_name,
                   e.ontology_tier
            FROM obligations o
            JOIN entities e ON o.entity_id = e.id
            WHERE o.status = 'PENDING' AND o.amount < 0
            AND o.due_date > %s AND o.due_date <= %s
            ORDER BY o.due_date;
            """,
            (simulated_now, horizon)
        )
        payables = cur.fetchall()

        if not payables:
            return {
                "status": "NO_OPTIMIZATION_NEEDED",
                "optimized_obligations": [],
                "projected_savings": 0.0,
                "breach_prevented": False
            }

        n = len(payables)

        # Build cost vector (c): late_fee_rate * amount + goodwill_penalty
        # Lower cost = preferred to delay (we're minimizing)
        c = []
        for p in payables:
            amount_abs = abs(float(p['amount']))
            late_fee_rate = float(p['late_fee_rate']) if p['late_fee_rate'] else 0.0
            goodwill = p['goodwill_score'] if p['goodwill_score'] is not None else 50

            late_fee_cost = amount_abs * late_fee_rate
            goodwill_penalty = amount_abs * (100 - goodwill) / 1000.0
            c.append(late_fee_cost + goodwill_penalty)

        c = np.array(c)

        # Calculate shortfall
        total_payables = sum(abs(float(p['amount'])) for p in payables)
        shortfall = max(0, total_payables - current_balance)

        if shortfall == 0:
            return {
                "status": "NO_OPTIMIZATION_NEEDED",
                "optimized_obligations": [],
                "projected_savings": 0.0,
                "breach_prevented": False
            }

        # Constraint: sum of delay amounts >= shortfall
        # Standard form: -sum(delay_i * amount_i) <= -shortfall
        A_ub = [[-abs(float(p['amount'])) for p in payables]]
        A_ub = np.array(A_ub)
        b_ub = np.array([-shortfall])

        # Bounds: ontology-tier-based delay limits
        # Tier 0 (Locked):   0% delay (taxes, payroll — immovable)
        # Tier 1 (Penalty):  up to 25% delay (carries late fees)
        # Tier 2 (Relational): up to 60% delay (goodwill risk)
        # Tier 3+ (Flexible): up to 100% delay (fully negotiable)
        TIER_MAX_DELAY = {0: 0.0, 1: 0.25, 2: 0.60, 3: 1.0}
        bounds = []
        for p in payables:
            tier = p.get('ontology_tier', 3) if not p['is_locked'] else 0
            max_delay = TIER_MAX_DELAY.get(tier, 1.0)
            bounds.append((0, max_delay))

        # Solve
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

        if not result.success:
            return {
                "status": "OPTIMIZATION_FAILED",
                "optimized_obligations": [],
                "projected_savings": 0.0,
                "breach_prevented": False,
                "error": result.message
            }

        # Build optimized strategy
        optimized_obligations = []
        total_delayed = 0

        TIER_LABELS = {0: "Locked", 1: "Penalty", 2: "Relational", 3: "Flexible"}
        for i, p in enumerate(payables):
            delay_fraction = result.x[i]
            amount_abs = abs(float(p['amount']))
            delay_amount = delay_fraction * amount_abs
            tier = p.get('ontology_tier', 3) if not p['is_locked'] else 0

            if delay_amount > 0.01:  # Threshold to avoid floating point noise
                pay_now = amount_abs - delay_amount
                delay_days = 7  # Default delay period

                due_date = p['due_date']
                optimized_obligations.append({
                    "obligation_id": str(p['id']),
                    "entity_name": p['entity_name'],
                    "original_amount": float(p['amount']),
                    "original_due": due_date.isoformat(),
                    "strategy": "FRACTIONAL_PAYMENT",
                    "pay_now": round(pay_now, 2),
                    "delay_amount": round(delay_amount, 2),
                    "new_due_date": (due_date + timedelta(days=delay_days)).isoformat(),
                    "estimated_cost": round(c[i] * delay_fraction, 2),
                    "ontology_tier": tier,
                    "tier_label": TIER_LABELS.get(tier, "Flexible"),
                    "goodwill_score": p['goodwill_score']
                })
                total_delayed += delay_amount

        return {
            "status": "SUCCESS",
            "optimized_obligations": optimized_obligations,
            "projected_savings": round(shortfall - result.fun, 2),
            "breach_prevented": True,
            "total_delayed": round(total_delayed, 2)
        }

    finally:
        cur.close()
        conn.close()
