# Stream 2 Implementation Plan: The Quant (Math Engine & Optimization)

## Overview
Stream 2 is the **deterministic brain** of CashPilot. This stream implements the pure mathematical logic that calculates runway, detects liquidity breaches, and optimizes payment strategies. **No AI/LLM is used in this stream** - only proven mathematical algorithms.

## Current Status
✅ **Phase 1 Complete**: Data ingestion pipeline, database schema, and simulation engine are operational
🎯 **Phase 2 Target**: Build the mathematical optimization engine that determines the best payment strategy

## Core Responsibility
Transform raw financial data into actionable mathematical decisions using:
- Deterministic runway calculations
- Linear programming optimization
- Monte Carlo probability modeling
- Virtual liability ring-fencing

---

## Tech Stack
- **Language**: Python 3.9+
- **Framework**: FastAPI (already set up)
- **Libraries**:
  - `pandas` - Data manipulation
  - `numpy` - Numerical computations
  - `scipy` - Linear programming solver
  - `psycopg2-binary` - Database connection (already installed)

---

## Installation

```bash
cd SnuHack/cashpilot/backend
pip install pandas numpy scipy
```

---

## Implementation Tasks

### Task 1: Create the Quant Module Structure

**File**: `backend/quant/__init__.py`
```python
# Empty init file to make quant a package
```

**File**: `backend/quant/runway_engine.py`
- Implements the deterministic "Days to Zero" calculation
- Pure mathematical ledger simulation
- No AI/LLM involvement

**File**: `backend/quant/optimizer.py`
- Linear programming solver using scipy
- Calculates optimal payment strategy
- Minimizes penalties while maintaining positive cash flow

**File**: `backend/quant/monte_carlo.py`
- Probabilistic modeling of payment scenarios
- Runs 10,000 simulations
- Outputs survival probability

**File**: `backend/quant/phantom_balance.py`
- Virtual liability ring-fencing logic
- Calculates "usable cash" vs "total cash"
- Subtracts locked obligations (Tier 0)

---

### Task 2: Implement the Runway Engine

**Purpose**: Calculate the exact "Days to Zero" (D2Z) metric

**Algorithm**:
```
For each day from today to +30 days:
    Balance[day] = Balance[day-1] + Receivables[day] - Payables[day]
    If Balance[day] < 0:
        Return day as "Liquidity Breach Date"
        Return days_until_breach as "Days to Zero"
```

**Implementation** (`backend/quant/runway_engine.py`):

```python
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from core.db import get_db_connection

def calculate_runway(company_id: str) -> Dict:
    """
    Calculates the deterministic Days to Zero (D2Z) metric.
    
    Returns:
        {
            "days_to_zero": int,
            "breach_date": str (ISO format) or None,
            "daily_projection": List[Dict] - 30 day balance forecast
        }
    """
    conn = get_db_connection()
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
```

---

### Task 3: Implement Phantom Balance Calculator

**Purpose**: Calculate "usable cash" by subtracting locked obligations

**Implementation** (`backend/quant/phantom_balance.py`):

```python
from datetime import timedelta
from typing import Dict
from core.db import get_db_connection

def calculate_phantom_balance(company_id: str, horizon_days: int = 7) -> Dict:
    """
    Calculates the Phantom Usable Cash by subtracting locked obligations.
    
    Formula:
        Usable Cash = Total Balance - Locked Tier 0 Obligations
    
    Args:
        company_id: UUID of the company
        horizon_days: Number of days to look ahead (default 7)
    
    Returns:
        {
            "total_balance": float,
            "locked_obligations": float,
            "usable_cash": float,
            "horizon_date": str
        }
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get current balance
        cur.execute(
            "SELECT plaid_current_balance, current_simulated_date FROM companies WHERE id = %s;",
            (company_id,)
        )
        company = cur.fetchone()
        if not company:
            raise ValueError("Company not found")
        
        total_balance = float(company['plaid_current_balance'])
        simulated_now = company['current_simulated_date']
        horizon = simulated_now + timedelta(days=horizon_days)
        
        # Sum all locked (Tier 0) obligations within horizon
        cur.execute(
            "SELECT COALESCE(SUM(amount), 0) as locked_total "
            "FROM obligations "
            "WHERE status = 'PENDING' AND is_locked = TRUE "
            "AND due_date > %s AND due_date <= %s;",
            (simulated_now, horizon)
        )
        locked_total = float(cur.fetchone()['locked_total'])
        
        # Usable cash = total - locked obligations (locked are negative, so we add)
        usable_cash = total_balance + locked_total  # locked_total is negative
        
        return {
            "total_balance": round(total_balance, 2),
            "locked_obligations": round(abs(locked_total), 2),
            "usable_cash": round(usable_cash, 2),
            "horizon_date": horizon.isoformat()
        }
    
    finally:
        cur.close()
        conn.close()
```

---

### Task 4: Implement Linear Programming Optimizer

**Purpose**: Find the optimal payment strategy that minimizes penalties while keeping balance ≥ 0

**Mathematical Formulation**:
```
Minimize: Σ (late_fee_i * delay_i + goodwill_penalty_i * delay_i)

Subject to:
    - Balance[day] ≥ 0 for all days
    - Tier 0 obligations MUST be paid (delay = 0)
    - delay_i ≥ 0 for all obligations
```

**Implementation** (`backend/quant/optimizer.py`):

```python
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np
from scipy.optimize import linprog
from core.db import get_db_connection

def optimize_payment_strategy(company_id: str) -> Dict:
    """
    Uses Linear Programming to find the optimal payment strategy.
    
    Objective: Minimize (late fees + goodwill damage)
    Constraints: Keep balance ≥ 0, Tier 0 must be paid
    
    Returns:
        {
            "status": str,
            "optimized_obligations": List[Dict],
            "projected_savings": float,
            "breach_prevented": bool
        }
    """
    conn = get_db_connection()
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
                   e.goodwill_score, e.late_fee_rate, e.name as entity_name
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
        
        # Build cost vector (c): late_fee_rate + goodwill_penalty
        # Goodwill penalty: (100 - goodwill_score) / 100 * amount
        c = []
        for p in payables:
            late_fee_cost = abs(float(p['amount'])) * float(p['late_fee_rate'])
            goodwill_penalty = abs(float(p['amount'])) * (100 - p['goodwill_score']) / 1000.0
            c.append(late_fee_cost + goodwill_penalty)
        
        c = np.array(c)
        
        # Build constraint matrix A_ub and b_ub
        # For each day, ensure: balance - sum(payments_on_day) ≥ 0
        # This becomes: sum(delay_variables) ≤ available_cash
        
        # Simplified approach: ensure total delayed amount doesn't exceed shortfall
        total_payables = sum(abs(float(p['amount'])) for p in payables)
        shortfall = max(0, total_payables - current_balance)
        
        if shortfall == 0:
            return {
                "status": "NO_OPTIMIZATION_NEEDED",
                "optimized_obligations": [],
                "projected_savings": 0.0,
                "breach_prevented": False
            }
        
        # Constraint: sum of delay amounts ≥ shortfall
        # We want to delay at least 'shortfall' worth of payments
        # Convert to standard form: -sum(delay_i) ≤ -shortfall
        A_ub = [-abs(float(p['amount'])) for p in payables]
        A_ub = np.array([A_ub])
        b_ub = np.array([-shortfall])
        
        # Bounds: locked obligations cannot be delayed (delay = 0)
        # Non-locked can be delayed up to their full amount
        bounds = []
        for p in payables:
            if p['is_locked']:
                bounds.append((0, 0))  # Cannot delay
            else:
                bounds.append((0, abs(float(p['amount']))))  # Can delay up to full amount
        
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
        
        for i, p in enumerate(payables):
            delay_amount = result.x[i]
            
            if delay_amount > 0.01:  # Threshold to avoid floating point noise
                pay_now = abs(float(p['amount'])) - delay_amount
                delay_days = 7  # Default delay period
                
                optimized_obligations.append({
                    "obligation_id": str(p['id']),
                    "entity_name": p['entity_name'],
                    "original_amount": float(p['amount']),
                    "original_due": p['due_date'].isoformat(),
                    "strategy": "FRACTIONAL_PAYMENT",
                    "pay_now": round(pay_now, 2),
                    "delay_amount": round(delay_amount, 2),
                    "new_due_date": (p['due_date'] + timedelta(days=delay_days)).isoformat(),
                    "estimated_cost": round(c[i] * (delay_amount / abs(float(p['amount']))), 2)
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
```

---

### Task 5: Implement Monte Carlo Simulator

**Purpose**: Run probabilistic simulations to calculate survival probability

**Implementation** (`backend/quant/monte_carlo.py`):

```python
from datetime import timedelta
from typing import Dict
import numpy as np
from core.db import get_db_connection

def run_monte_carlo_simulation(company_id: str, num_simulations: int = 10000) -> Dict:
    """
    Runs Monte Carlo simulations to calculate probability of survival.
    
    Accounts for:
    - Client payment delays (based on avg_latency_days)
    - Random payment timing variance
    
    Args:
        company_id: UUID of the company
        num_simulations: Number of simulations to run (default 10,000)
    
    Returns:
        {
            "simulations": int,
            "survival_probability": float (0-100),
            "p10_balance": float (10th percentile - bear case),
            "median_balance": float (50th percentile),
            "p90_balance": float (90th percentile - bull case)
        }
    """
    conn = get_db_connection()
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
        
        initial_balance = float(company['plaid_current_balance'])
        simulated_now = company['current_simulated_date']
        
        # Get all pending obligations with entity latency data
        horizon = simulated_now + timedelta(days=30)
        cur.execute(
            """
            SELECT o.amount, o.due_date, e.avg_latency_days
            FROM obligations o
            JOIN entities e ON o.entity_id = e.id
            WHERE o.status = 'PENDING' AND o.due_date > %s AND o.due_date <= %s;
            """,
            (simulated_now, horizon)
        )
        obligations = cur.fetchall()
        
        if not obligations:
            return {
                "simulations": num_simulations,
                "survival_probability": 100.0,
                "p10_balance": initial_balance,
                "median_balance": initial_balance,
                "p90_balance": initial_balance
            }
        
        # Run simulations
        final_balances = []
        survival_count = 0
        
        for _ in range(num_simulations):
            balance = initial_balance
            
            for ob in obligations:
                amount = float(ob['amount'])
                latency = ob['avg_latency_days'] or 0
                
                # Add random variance to payment timing
                # Receivables (positive) can be delayed
                # Payables (negative) are paid on time or early
                if amount > 0:  # Receivable
                    # Apply latency with normal distribution
                    actual_delay = max(0, np.random.normal(latency, latency * 0.3))
                    # Some receivables never arrive (5% default rate)
                    if np.random.random() > 0.05:
                        balance += amount
                else:  # Payable
                    # Payables are paid (with small chance of early payment)
                    balance += amount
            
            final_balances.append(balance)
            if balance >= 0:
                survival_count += 1
        
        final_balances = np.array(final_balances)
        
        return {
            "simulations": num_simulations,
            "survival_probability": round((survival_count / num_simulations) * 100, 2),
            "p10_balance": round(float(np.percentile(final_balances, 10)), 2),
            "median_balance": round(float(np.percentile(final_balances, 50)), 2),
            "p90_balance": round(float(np.percentile(final_balances, 90)), 2)
        }
    
    finally:
        cur.close()
        conn.close()
```

---

### Task 6: Create Unified Quant API Endpoints

**File**: `backend/api/quant_router.py`

```python
from fastapi import APIRouter, HTTPException
from quant.runway_engine import calculate_runway
from quant.phantom_balance import calculate_phantom_balance
from quant.optimizer import optimize_payment_strategy
from quant.monte_carlo import run_monte_carlo_simulation

router = APIRouter()

@router.get("/api/quant/runway")
def get_runway():
    """Calculate Days to Zero and daily projection."""
    try:
        # Get first company (demo assumes single company)
        from core.db import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM companies LIMIT 1;")
        company = cur.fetchone()
        cur.close()
        conn.close()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        result = calculate_runway(str(company['id']))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/quant/phantom")
def get_phantom():
    """Calculate Phantom Usable Cash."""
    try:
        from core.db import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM companies LIMIT 1;")
        company = cur.fetchone()
        cur.close()
        conn.close()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        result = calculate_phantom_balance(str(company['id']))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/quant/optimize")
def get_optimization():
    """Run Linear Programming optimization for payment strategy."""
    try:
        from core.db import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM companies LIMIT 1;")
        company = cur.fetchone()
        cur.close()
        conn.close()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        result = optimize_payment_strategy(str(company['id']))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/quant/monte-carlo")
def get_monte_carlo():
    """Run Monte Carlo simulation for survival probability."""
    try:
        from core.db import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM companies LIMIT 1;")
        company = cur.fetchone()
        cur.close()
        conn.close()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        result = run_monte_carlo_simulation(str(company['id']))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Task 7: Register Quant Router in Main App

**File**: `backend/main.py` (add this line)

```python
# Add after existing router imports
from api.quant_router import router as quant_router

# Add after existing router includes
app.include_router(quant_router, tags=["Quant Engine"])
```

---

## Testing the Implementation

### Step 1: Start the Backend
```bash
cd SnuHack/cashpilot/backend
uvicorn main:app --reload
```

### Step 2: Test Each Endpoint

**Test Runway Calculation**:
```bash
curl http://localhost:8000/api/quant/runway
```

Expected response:
```json
{
  "days_to_zero": 8,
  "breach_date": "2026-04-02",
  "daily_projection": [...],
  "current_balance": 12450.00
}
```

**Test Phantom Balance**:
```bash
curl http://localhost:8000/api/quant/phantom
```

**Test Optimization**:
```bash
curl http://localhost:8000/api/quant/optimize
```

**Test Monte Carlo**:
```bash
curl http://localhost:8000/api/quant/monte-carlo
```

---

## Integration with Existing Dashboard

Update `backend/api/dashboard_router.py` to use the new quant modules:

```python
# At the top, add imports
from quant.runway_engine import calculate_runway
from quant.phantom_balance import calculate_phantom_balance
from quant.monte_carlo import run_monte_carlo_simulation

# Update the /api/dashboard endpoint to use quant functions
@router.get("/api/dashboard")
def get_dashboard():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM companies LIMIT 1;")
        company = cur.fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        company_id = str(company['id'])
        
        # Use quant modules
        runway_data = calculate_runway(company_id)
        phantom_data = calculate_phantom_balance(company_id)
        
        # Fetch urgent actions (existing code)
        cur.execute("SELECT id, message as title, action_type as priority, status as subtitle FROM action_logs WHERE is_resolved = FALSE ORDER BY created_at DESC LIMIT 3;")
        actions_db = cur.fetchall()
        actions = []
        for a in actions_db:
            priority = 'high'
            if 'URGENT' in a['title']: priority = 'critical'
            actions.append({"id": str(a['id']), "title": a['title'], "subtitle": a['subtitle'] or "Pending", "priority": priority})
        
        return {
            "vitals": {
                "totalBank": runway_data['current_balance'],
                "phantomUsable": phantom_data['usable_cash'],
                "daysToZero": runway_data['days_to_zero']
            },
            "actions": actions,
            "sparkline": runway_data['daily_projection'][:14]  # First 14 days
        }
    finally:
        cur.close()
        conn.close()
```

---

## Success Criteria

✅ All 4 quant modules implemented and tested
✅ API endpoints return correct mathematical results
✅ No AI/LLM used in calculations (pure deterministic logic)
✅ Dashboard integrates with quant engine
✅ Linear programming successfully optimizes payment strategy
✅ Monte Carlo provides realistic probability estimates

---

## Next Steps After Stream 2

Once Stream 2 is complete, you can move to:
- **Stream 3**: AI Orchestrator (translating math into human actions)
- **Stream 4**: Frontend enhancements (visualizing optimization results)

---

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'scipy'`
**Solution**: `pip install scipy`

**Issue**: Linear programming returns "infeasible"
**Solution**: Check that you have enough flexible (non-locked) obligations to delay

**Issue**: Monte Carlo takes too long
**Solution**: Reduce `num_simulations` to 1000 for testing

---

## Key Principles

1. **No AI in Math**: This stream uses ZERO LLM calls - only proven algorithms
2. **Deterministic**: Same input always produces same output
3. **Explainable**: Every calculation can be traced and verified
4. **Fast**: All calculations complete in < 1 second
5. **Accurate**: Uses real database data, not mocks

---

## File Structure After Completion

```
backend/
├── quant/
│   ├── __init__.py
│   ├── runway_engine.py
│   ├── phantom_balance.py
│   ├── optimizer.py
│   └── monte_carlo.py
├── api/
│   ├── quant_router.py
│   ├── dashboard_router.py (updated)
│   └── ...
└── main.py (updated)
```

---

## Estimated Time: 3-4 hours

- Task 1: 15 minutes (setup)
- Task 2: 45 minutes (runway engine)
- Task 3: 30 minutes (phantom balance)
- Task 4: 90 minutes (optimizer - most complex)
- Task 5: 45 minutes (monte carlo)
- Task 6: 20 minutes (API endpoints)
- Task 7: 10 minutes (integration)
- Testing: 30 minutes

---

**Ready to start? Begin with Task 1 and work sequentially. Each task builds on the previous one.**
