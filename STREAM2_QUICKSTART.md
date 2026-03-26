# Stream 2 Quick Start Guide

## What is Stream 2?

Stream 2 is the **mathematical brain** of CashPilot. It takes the financial data from Stream 1 and performs pure mathematical calculations to:

1. Calculate "Days to Zero" (when you'll run out of money)
2. Determine "Phantom Usable Cash" (money you can actually spend)
3. Optimize payment strategies using Linear Programming
4. Run Monte Carlo simulations for probability analysis

**CRITICAL**: Stream 2 uses **ZERO AI/LLM** - only proven mathematical algorithms.

---

## Prerequisites

✅ Phase 1 complete (database, ingestion pipeline working)
✅ Backend server running
✅ Python 3.9+ installed

---

## Installation (2 minutes)

```bash
cd SnuHack/cashpilot/backend
pip install pandas numpy scipy
```

---

## Implementation Checklist

### Core Files to Create:

- [ ] `backend/quant/__init__.py` (empty file)
- [ ] `backend/quant/runway_engine.py` (Days to Zero calculation)
- [ ] `backend/quant/phantom_balance.py` (Usable cash calculation)
- [ ] `backend/quant/optimizer.py` (Linear programming solver)
- [ ] `backend/quant/monte_carlo.py` (Probability simulations)
- [ ] `backend/api/quant_router.py` (API endpoints)

### Integration:

- [ ] Update `backend/main.py` to include quant router
- [ ] Update `backend/api/dashboard_router.py` to use quant functions

---

## Quick Test

After implementation, test with:

```bash
# Start server
cd SnuHack/cashpilot/backend
uvicorn main:app --reload

# In another terminal, test endpoints:
curl http://localhost:8000/api/quant/runway
curl http://localhost:8000/api/quant/phantom
curl http://localhost:8000/api/quant/optimize
curl http://localhost:8000/api/quant/monte-carlo
```

---

## What Each Module Does

### 1. Runway Engine (`runway_engine.py`)
**Input**: Current balance + pending obligations
**Output**: Days until balance hits $0
**Algorithm**: Day-by-day ledger simulation

### 2. Phantom Balance (`phantom_balance.py`)
**Input**: Total balance + locked obligations (taxes, payroll)
**Output**: Money you can actually spend
**Formula**: `Usable = Total - Locked`

### 3. Optimizer (`optimizer.py`)
**Input**: Payables + vendor goodwill scores
**Output**: Optimal payment strategy (who to pay, who to delay)
**Algorithm**: Linear Programming (scipy.optimize.linprog)

### 4. Monte Carlo (`monte_carlo.py`)
**Input**: Obligations + payment latency data
**Output**: Probability of survival (0-100%)
**Algorithm**: 10,000 randomized simulations

---

## Expected Results

### Runway Engine Response:
```json
{
  "days_to_zero": 8,
  "breach_date": "2026-04-02",
  "current_balance": 12450.00,
  "daily_projection": [...]
}
```

### Phantom Balance Response:
```json
{
  "total_balance": 12450.00,
  "locked_obligations": 8350.00,
  "usable_cash": 4100.00
}
```

### Optimizer Response:
```json
{
  "status": "SUCCESS",
  "optimized_obligations": [
    {
      "entity_name": "Acme Supplies",
      "strategy": "FRACTIONAL_PAYMENT",
      "pay_now": 100.00,
      "delay_amount": 300.00
    }
  ],
  "breach_prevented": true
}
```

### Monte Carlo Response:
```json
{
  "simulations": 10000,
  "survival_probability": 82.5,
  "p10_balance": -500.00,
  "median_balance": 2100.00,
  "p90_balance": 5200.00
}
```

---

## Time Estimate

- **Setup**: 15 minutes
- **Core Implementation**: 3 hours
- **Testing**: 30 minutes
- **Total**: ~4 hours

---

## Key Principles

1. ✅ **Deterministic**: Same input = same output (no randomness except Monte Carlo)
2. ✅ **Fast**: All calculations < 1 second
3. ✅ **No AI**: Pure math only
4. ✅ **Explainable**: Every number can be traced
5. ✅ **Database-driven**: Uses real data from Supabase

---

## Common Issues

**Problem**: `ModuleNotFoundError: No module named 'scipy'`
**Fix**: `pip install scipy`

**Problem**: Optimizer returns "infeasible"
**Fix**: Ensure you have non-locked obligations that can be delayed

**Problem**: Monte Carlo is slow
**Fix**: Reduce simulations to 1000 for testing

---

## Success Criteria

You're done when:
- ✅ All 4 API endpoints return valid JSON
- ✅ Dashboard shows correct Days to Zero
- ✅ Optimizer suggests payment strategies
- ✅ Monte Carlo shows survival probability
- ✅ No errors in console

---

## Next Steps

After Stream 2 is complete:
1. **Stream 3**: AI Orchestrator (draft emails based on math)
2. **Stream 4**: Frontend visualization (charts, graphs)

---

## Need Help?

Refer to the full `stream2_plan.md` for:
- Complete code implementations
- Detailed algorithm explanations
- Integration instructions
- Advanced troubleshooting

---

**Start with Task 1 in `stream2_plan.md` and work sequentially!**
