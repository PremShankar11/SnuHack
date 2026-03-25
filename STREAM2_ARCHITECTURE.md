# Stream 2 Architecture Overview

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         STREAM 2: THE QUANT                      │
│                    (Pure Mathematical Engine)                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   DATABASE   │
│  (Supabase)  │
│              │
│ • companies  │
│ • entities   │
│ • obligations│
│ • transactions│
└──────┬───────┘
       │
       │ SQL Queries
       ↓
┌──────────────────────────────────────────────────────────────────┐
│                      QUANT MODULE (Python)                        │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ Runway Engine  │  │ Phantom Balance│  │   Optimizer      │  │
│  │                │  │                │  │                  │  │
│  │ • Daily ledger │  │ • Total balance│  │ • Linear Prog    │  │
│  │ • Breach detect│  │ • Locked funds │  │ • Minimize cost  │  │
│  │ • Days to Zero │  │ • Usable cash  │  │ • Payment plan   │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Monte Carlo Simulator                          │ │
│  │                                                             │ │
│  │  • 10,000 simulations                                      │ │
│  │  • Payment timing variance                                 │ │
│  │  • Survival probability                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ JSON Results
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│                    FASTAPI ENDPOINTS                              │
│                                                                   │
│  GET /api/quant/runway       → Days to Zero + projection         │
│  GET /api/quant/phantom      → Usable cash calculation           │
│  GET /api/quant/optimize     → Optimal payment strategy          │
│  GET /api/quant/monte-carlo  → Survival probability              │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                             │
│                                                                   │
│  • Dashboard displays Days to Zero                               │
│  • Charts show Phantom vs Total balance                          │
│  • Action inbox shows optimization suggestions                   │
│  • Analytics page shows Monte Carlo results                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Example

### Scenario: User moves simulation slider to Day +10

```
1. Frontend sends: POST /api/simulate/advance {"days_offset": 10}
   ↓
2. Simulation Router updates database:
   - Marks obligations as PAID
   - Updates balance
   - Generates new obligations
   ↓
3. Frontend requests: GET /api/dashboard
   ↓
4. Dashboard Router calls Quant modules:
   
   a) calculate_runway(company_id)
      → Queries obligations table
      → Simulates 30-day ledger
      → Returns: days_to_zero = 5, breach_date = "2026-04-05"
   
   b) calculate_phantom_balance(company_id)
      → Queries locked obligations
      → Calculates: usable = total - locked
      → Returns: usable_cash = 2100.00
   
   c) (Optional) optimize_payment_strategy(company_id)
      → Queries payables + goodwill scores
      → Runs Linear Programming
      → Returns: optimal payment plan
   
   d) (Optional) run_monte_carlo_simulation(company_id)
      → Queries obligations + latency data
      → Runs 10,000 simulations
      → Returns: survival_probability = 65%
   ↓
5. Dashboard Router combines results into JSON
   ↓
6. Frontend displays:
   - "5 Days to Zero" (red alert)
   - "$2,100 Usable Cash" (vs $8,500 total)
   - "65% Survival Probability"
   - Action: "Delay Acme Supplies payment by 7 days"
```

---

## Module Dependencies

```
runway_engine.py
├── Depends on: core.db (database connection)
├── Reads: companies, obligations tables
└── Returns: Dict with days_to_zero, breach_date, projection

phantom_balance.py
├── Depends on: core.db
├── Reads: companies, obligations (filtered by is_locked)
└── Returns: Dict with total, locked, usable

optimizer.py
├── Depends on: core.db, scipy.optimize.linprog
├── Reads: companies, obligations, entities (goodwill, late_fee_rate)
└── Returns: Dict with optimized payment strategy

monte_carlo.py
├── Depends on: core.db, numpy
├── Reads: companies, obligations, entities (avg_latency_days)
└── Returns: Dict with survival probability, percentiles
```

---

## Mathematical Algorithms

### 1. Runway Engine (Deterministic)

```python
# Pseudocode
balance = current_balance
for day in range(30):
    obligations_due_today = get_obligations(day)
    balance += sum(obligations_due_today)
    
    if balance < 0:
        return days_to_zero = day
        
return days_to_zero = 30  # No breach
```

**Complexity**: O(n) where n = number of obligations
**Runtime**: < 100ms

---

### 2. Phantom Balance (Simple Subtraction)

```python
# Pseudocode
total_balance = get_current_balance()
locked_obligations = sum(
    obligations 
    where is_locked = TRUE 
    and due_date <= horizon
)

usable_cash = total_balance - abs(locked_obligations)
```

**Complexity**: O(1) - single query
**Runtime**: < 50ms

---

### 3. Linear Programming Optimizer

```python
# Pseudocode
# Objective: Minimize cost
cost = late_fees + goodwill_penalties

# Constraints:
# 1. Balance must stay >= 0
# 2. Locked obligations cannot be delayed
# 3. Delay amount <= obligation amount

result = scipy.optimize.linprog(
    c=cost_vector,
    A_ub=constraint_matrix,
    b_ub=constraint_bounds,
    bounds=delay_bounds
)

# Result: optimal delay amounts for each obligation
```

**Complexity**: O(n³) for simplex method
**Runtime**: < 500ms for typical problem size

---

### 4. Monte Carlo Simulation

```python
# Pseudocode
survival_count = 0

for simulation in range(10000):
    balance = current_balance
    
    for obligation in obligations:
        # Add random variance
        if obligation.type == 'receivable':
            delay = random.normal(avg_latency, std_dev)
            if random() > 0.05:  # 5% default rate
                balance += obligation.amount
        else:  # payable
            balance += obligation.amount
    
    if balance >= 0:
        survival_count += 1

survival_probability = survival_count / 10000 * 100
```

**Complexity**: O(n × m) where n = obligations, m = simulations
**Runtime**: < 2 seconds for 10,000 simulations

---

## API Response Formats

### Runway Engine
```json
{
  "days_to_zero": 8,
  "breach_date": "2026-04-02",
  "current_balance": 12450.00,
  "daily_projection": [
    {"date": "2026-03-25", "balance": 12450.00, "day_net": 0},
    {"date": "2026-03-26", "balance": 12200.00, "day_net": -250},
    ...
  ]
}
```

### Phantom Balance
```json
{
  "total_balance": 12450.00,
  "locked_obligations": 8350.00,
  "usable_cash": 4100.00,
  "horizon_date": "2026-04-01"
}
```

### Optimizer
```json
{
  "status": "SUCCESS",
  "optimized_obligations": [
    {
      "obligation_id": "uuid-123",
      "entity_name": "Acme Supplies",
      "original_amount": -400.00,
      "original_due": "2026-03-27",
      "strategy": "FRACTIONAL_PAYMENT",
      "pay_now": 100.00,
      "delay_amount": 300.00,
      "new_due_date": "2026-04-03",
      "estimated_cost": 12.50
    }
  ],
  "projected_savings": 187.50,
  "breach_prevented": true,
  "total_delayed": 300.00
}
```

### Monte Carlo
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

## Integration Points

### With Stream 1 (Data Ingestion)
- **Input**: Stream 1 populates `obligations` table
- **Output**: Stream 2 reads from `obligations` table
- **Contract**: Both use same database schema

### With Stream 3 (AI Orchestrator)
- **Input**: Stream 2 provides optimization results
- **Output**: Stream 3 drafts emails based on math
- **Contract**: JSON format from optimizer → AI prompt

### With Stream 4 (Frontend)
- **Input**: Frontend calls `/api/quant/*` endpoints
- **Output**: Stream 2 returns JSON
- **Contract**: Standardized JSON response formats

---

## Performance Benchmarks

| Module | Typical Runtime | Max Runtime |
|--------|----------------|-------------|
| Runway Engine | 50ms | 200ms |
| Phantom Balance | 30ms | 100ms |
| Optimizer | 200ms | 1000ms |
| Monte Carlo | 1500ms | 3000ms |

**Total Dashboard Load**: < 2 seconds (all modules combined)

---

## Error Handling

### Database Connection Failure
```python
conn = get_db_connection()
if not conn:
    raise HTTPException(status_code=500, detail="Database connection failed")
```

### No Company Found
```python
if not company:
    raise HTTPException(status_code=404, detail="Company not found")
```

### Optimization Infeasible
```python
if not result.success:
    return {
        "status": "OPTIMIZATION_FAILED",
        "error": result.message
    }
```

---

## Testing Strategy

### Unit Tests (Recommended)
```python
def test_runway_engine():
    # Setup: Create test company with known obligations
    # Execute: calculate_runway(test_company_id)
    # Assert: days_to_zero matches expected value

def test_phantom_balance():
    # Setup: Create company with locked obligations
    # Execute: calculate_phantom_balance(test_company_id)
    # Assert: usable_cash = total - locked

def test_optimizer():
    # Setup: Create shortfall scenario
    # Execute: optimize_payment_strategy(test_company_id)
    # Assert: breach_prevented = True
```

### Integration Tests
```bash
# Test full flow
curl http://localhost:8000/api/quant/runway
curl http://localhost:8000/api/quant/optimize
# Verify: optimizer uses runway data correctly
```

---

## Deployment Checklist

- [ ] All dependencies installed (`pandas`, `numpy`, `scipy`)
- [ ] Database connection working
- [ ] All 4 modules implemented
- [ ] API endpoints registered in `main.py`
- [ ] Dashboard router updated to use quant functions
- [ ] All endpoints return valid JSON
- [ ] No errors in console logs
- [ ] Performance < 2 seconds for dashboard load

---

## Key Takeaways

1. **Pure Math**: No AI/LLM in Stream 2 - only deterministic algorithms
2. **Fast**: All calculations complete in < 2 seconds
3. **Accurate**: Uses real database data, not mocks
4. **Explainable**: Every number can be traced to source
5. **Modular**: Each function is independent and testable

---

**Ready to implement? Start with `stream2_plan.md` Task 1!**
