# Stream 2 Implementation - Complete Guide

## 📋 Overview

You've successfully completed **Phase 1** (Data Ingestion & Simulation). Now it's time to build **Stream 2: The Quant Engine** - the mathematical brain that transforms raw financial data into actionable decisions.

## 🎯 What You're Building

Stream 2 implements 4 core mathematical engines:

1. **Runway Engine** - Calculates "Days to Zero" (when cash runs out)
2. **Phantom Balance** - Determines actual spendable cash (total - locked obligations)
3. **Linear Programming Optimizer** - Finds optimal payment strategy to avoid bankruptcy
4. **Monte Carlo Simulator** - Calculates probability of survival using 10,000 simulations

**CRITICAL**: Stream 2 uses **ZERO AI/LLM** - only proven mathematical algorithms.

---

## 📚 Documentation Files

I've created 3 comprehensive documents for you:

### 1. `stream2_plan.md` - Full Implementation Guide
- **Purpose**: Step-by-step implementation instructions
- **Contains**: Complete code for all 4 modules + API endpoints
- **Use when**: Actually writing the code
- **Time**: 3-4 hours to complete

### 2. `STREAM2_QUICKSTART.md` - Quick Reference
- **Purpose**: Fast overview and testing guide
- **Contains**: Installation, checklist, expected outputs
- **Use when**: Need quick reference or testing
- **Time**: 2-minute read

### 3. `STREAM2_ARCHITECTURE.md` - System Design
- **Purpose**: Understand how everything connects
- **Contains**: Flow diagrams, algorithms, performance benchmarks
- **Use when**: Need to understand the big picture
- **Time**: 5-minute read

---

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
cd SnuHack/cashpilot/backend
pip install pandas numpy scipy
```

### Step 2: Create Module Structure
```bash
mkdir -p backend/quant
touch backend/quant/__init__.py
```

### Step 3: Follow Implementation Plan
Open `stream2_plan.md` and follow Tasks 1-7 sequentially.

---

## 📊 Current Project Status

### ✅ Completed (Phase 1)
- Database schema (Supabase)
- Data ingestion pipeline (receipt OCR, Plaid simulator)
- Simulation engine (time travel slider)
- Basic dashboard API
- Frontend UI (Next.js)

### 🎯 To Complete (Stream 2)
- [ ] Runway engine (`quant/runway_engine.py`)
- [ ] Phantom balance calculator (`quant/phantom_balance.py`)
- [ ] Linear programming optimizer (`quant/optimizer.py`)
- [ ] Monte Carlo simulator (`quant/monte_carlo.py`)
- [ ] Quant API endpoints (`api/quant_router.py`)
- [ ] Dashboard integration (update `api/dashboard_router.py`)

---

## 🏗️ File Structure

### Before Stream 2:
```
backend/
├── api/
│   ├── router.py (ingestion)
│   ├── simulation_router.py
│   └── dashboard_router.py
├── core/
│   └── db.py
├── scripts/
│   └── ... (seed data, simulators)
└── main.py
```

### After Stream 2:
```
backend/
├── api/
│   ├── router.py
│   ├── simulation_router.py
│   ├── dashboard_router.py
│   └── quant_router.py ← NEW
├── core/
│   └── db.py
├── quant/ ← NEW FOLDER
│   ├── __init__.py
│   ├── runway_engine.py
│   ├── phantom_balance.py
│   ├── optimizer.py
│   └── monte_carlo.py
├── scripts/
│   └── ...
└── main.py (updated)
```

---

## 🧪 Testing Your Implementation

### Test 1: Runway Engine
```bash
curl http://localhost:8000/api/quant/runway
```
**Expected**: JSON with `days_to_zero`, `breach_date`, `daily_projection`

### Test 2: Phantom Balance
```bash
curl http://localhost:8000/api/quant/phantom
```
**Expected**: JSON with `total_balance`, `usable_cash`, `locked_obligations`

### Test 3: Optimizer
```bash
curl http://localhost:8000/api/quant/optimize
```
**Expected**: JSON with `optimized_obligations`, `breach_prevented`

### Test 4: Monte Carlo
```bash
curl http://localhost:8000/api/quant/monte-carlo
```
**Expected**: JSON with `survival_probability`, `p10`, `median`, `p90`

### Test 5: Integrated Dashboard
```bash
curl http://localhost:8000/api/dashboard
```
**Expected**: Dashboard now uses quant engine for accurate calculations

---

## 🎓 Key Concepts

### Days to Zero (D2Z)
The number of days until your cash balance hits $0 based on scheduled obligations.

**Formula**:
```
For each day:
    Balance[day] = Balance[day-1] + Receivables[day] - Payables[day]
    If Balance[day] < 0: return day
```

### Phantom Balance
The amount of cash you can actually spend after accounting for locked obligations (taxes, payroll).

**Formula**:
```
Usable Cash = Total Balance - Locked Obligations
```

### Linear Programming Optimization
Mathematical technique to find the best payment strategy.

**Objective**: Minimize (late fees + goodwill damage)
**Constraints**: 
- Balance must stay ≥ 0
- Tier 0 obligations cannot be delayed
- Delay amount ≤ obligation amount

### Monte Carlo Simulation
Runs 10,000 randomized scenarios to calculate probability of survival.

**Process**:
1. For each simulation, add random variance to payment timing
2. Calculate final balance
3. Count how many simulations end with balance ≥ 0
4. Survival probability = (successful simulations / total) × 100

---

## 🔧 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'scipy'`
**Solution**: 
```bash
pip install scipy
```

### Issue: Optimizer returns "OPTIMIZATION_FAILED"
**Possible causes**:
1. All obligations are locked (Tier 0) - nothing to optimize
2. Shortfall is too large - not enough flexible obligations
3. Database has no pending obligations

**Solution**: Check your database has non-locked obligations with `is_locked = FALSE`

### Issue: Monte Carlo is slow (> 5 seconds)
**Solution**: Reduce simulations for testing:
```python
# In monte_carlo.py
def run_monte_carlo_simulation(company_id: str, num_simulations: int = 1000):  # Changed from 10000
```

### Issue: Dashboard shows incorrect Days to Zero
**Solution**: Ensure `dashboard_router.py` is using the new quant functions:
```python
from quant.runway_engine import calculate_runway
runway_data = calculate_runway(company_id)
```

---

## 📈 Success Metrics

You've successfully completed Stream 2 when:

✅ All 4 quant modules are implemented
✅ All 4 API endpoints return valid JSON
✅ Dashboard displays accurate Days to Zero
✅ Optimizer suggests payment strategies when shortfall detected
✅ Monte Carlo shows realistic survival probability
✅ No errors in backend console
✅ All calculations complete in < 2 seconds

---

## 🎯 Next Steps After Stream 2

Once Stream 2 is complete, you can proceed to:

### Stream 3: AI Orchestrator
- Draft negotiation emails based on optimizer results
- Use Gemini API to generate context-aware messages
- Implement multi-agent negotiation system

### Stream 4: Frontend Enhancements
- Visualize optimization results
- Add interactive charts for Monte Carlo
- Build Chain-of-Thought UI for explainability

---

## 💡 Pro Tips

1. **Start Simple**: Implement runway engine first - it's the easiest
2. **Test Incrementally**: Test each module before moving to the next
3. **Use Real Data**: Don't mock - use actual database queries
4. **Keep It Fast**: All calculations should complete in < 1 second
5. **Document Assumptions**: Add comments explaining your math

---

## 📞 Need Help?

### Quick Questions
- Check `STREAM2_QUICKSTART.md` for common issues

### Implementation Details
- Refer to `stream2_plan.md` for complete code

### Architecture Questions
- Review `STREAM2_ARCHITECTURE.md` for system design

### Still Stuck?
- Check existing code in `backend/api/simulation_router.py` for patterns
- Review database schema in `schema.sql`
- Test database connection with `python -m scripts.check_db`

---

## 🏆 Why Stream 2 Matters

Stream 2 is the **core differentiator** for your hackathon project:

1. **Judges Love Math**: Deterministic algorithms prove you understand the problem
2. **No Hallucinations**: Pure math = reliable results
3. **Explainable**: Every number can be traced and verified
4. **Fast**: Sub-second response times
5. **Scalable**: Works for any business size

**Remember**: The hackathon prompt explicitly asks for "deterministic systems for projections and calculations, rather than relying solely on LLM-based reasoning."

Stream 2 is how you win that criterion.

---

## ⏱️ Time Allocation

| Task | Time | Priority |
|------|------|----------|
| Setup & Installation | 15 min | HIGH |
| Runway Engine | 45 min | HIGH |
| Phantom Balance | 30 min | HIGH |
| Optimizer | 90 min | MEDIUM |
| Monte Carlo | 45 min | LOW |
| API Endpoints | 20 min | HIGH |
| Integration | 10 min | HIGH |
| Testing | 30 min | HIGH |
| **TOTAL** | **~4 hours** | |

**Recommendation**: If time is limited, implement Runway + Phantom + API first. Add Optimizer and Monte Carlo later.

---

## 🎬 Getting Started

1. Read this document (you're here!)
2. Skim `STREAM2_ARCHITECTURE.md` to understand the big picture
3. Open `stream2_plan.md` and start with Task 1
4. Test each module as you complete it
5. Integrate with dashboard
6. Celebrate! 🎉

---

**Ready to build the mathematical brain of CashPilot? Open `stream2_plan.md` and let's go!**
