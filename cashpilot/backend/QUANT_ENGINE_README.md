# Quant Engine (Stream 2) - Documentation

## Overview

The Quant Engine is the deterministic core of the CashPilot Financial Autopilot system. It provides mathematical calculations for financial decision-making without any AI/LLM components.

## Architecture

```
backend/
├── quant/
│   ├── __init__.py
│   ├── runway.py              # Runway calculation
│   ├── phantom_balance.py     # Virtual liability ring-fencing
│   ├── monte_carlo.py         # Probabilistic simulation
│   └── optimizer.py           # Linear programming optimization
└── api/
    └── quant_routes.py        # FastAPI endpoints
```

## Modules

### 1. Runway Engine (`runway.py`)

Calculates days until cash balance reaches zero.

**Function:** `calculate_runway(balance, obligations)`

**Logic:**
- Sorts obligations by due_date
- Simulates daily balance trajectory
- Detects first date where balance < 0

**Returns:**
```json
{
  "days_to_zero": 15,
  "breach_date": "2026-04-09"
}
```

### 2. Phantom Balance (`phantom_balance.py`)

Calculates usable cash after ring-fencing Tier 0 obligations.

**Function:** `calculate_usable_cash(balance, obligations, entities)`

**Logic:**
- Identifies Tier 0 entities (ontology_tier == 0)
- Locks their obligation amounts
- Calculates remaining usable cash

**Returns:**
```json
{
  "usable_cash": 7000.00,
  "locked_amount": 3000.00
}
```

### 3. Monte Carlo Simulation (`monte_carlo.py`)

Probabilistic runway analysis with payment delay uncertainty.

**Function:** `monte_carlo_simulation(balance, obligations, entities, simulations=1000)`

**Logic:**
- Runs N simulations (default 1000)
- Applies random delays: delay ~ N(0, avg_latency_days)
- Counts survival rate (no negative balance)

**Returns:**
```json
{
  "survival_probability": 0.7234
}
```

### 4. Linear Programming Optimizer (`optimizer.py`)

Minimizes late fees + goodwill penalties using scipy.optimize.linprog.

**Function:** `optimize_payments(balance, obligations, entities)`

**Objective:**
```
Minimize: Σ(late_fee_cost + goodwill_penalty) * delay_fraction
```

**Constraints:**
- Sum of payments ≤ balance
- Tier 0 obligations must be fully paid (delay_fraction = 0)
- Other obligations: 0 ≤ delay_fraction ≤ 1

**Returns:**
```json
{
  "optimization_result": [
    {
      "obligation_id": "uuid",
      "entity_name": "Vendor A",
      "math_decision": "PARTIAL",
      "pay_now_amount": 1500.00,
      "delay_amount": 1000.00,
      "requested_extension_days": 7
    }
  ]
}
```

## API Endpoints

### GET /api/dashboard

Returns global financial state with runway metrics.

**Response:**
```json
{
  "global_state": {
    "simulated_as_of": "2026-03-25",
    "plaid_balance": 12450.00,
    "phantom_usable_cash": 4100.00,
    "locked_tier_0_funds": 8350.00,
    "runway_metrics": {
      "days_to_zero": 8,
      "liquidity_breach_date": "2026-04-02",
      "monte_carlo_survival_prob": 0.12
    },
    "cashflow_projection_array": [
      {
        "date": "2026-03-25",
        "balance": 4100.00
      },
      {
        "date": "2026-03-26",
        "balance": 4100.00
      },
      {
        "date": "2026-03-27",
        "balance": -200.00
      }
    ]
  }
}
```

### GET /api/decision

Returns optimization directive for payment decisions.

**Response:**
```json
{
  "solver_directive": {
    "breach_amount": -200.00,
    "optimization_result": [
      {
        "obligation_id": "uuid",
        "entity_name": "Acme Supplies",
        "original_due": "2026-03-27",
        "math_decision": "FRACTIONAL_PAYMENT",
        "pay_now_amount": 100.00,
        "delay_amount": 300.00,
        "requested_extension_days": 7
      }
    ]
  }
}
```

## Database Schema

The Quant Engine reads from these Supabase tables:

**companies:**
- plaid_current_balance (DECIMAL)

**entities:**
- ontology_tier (INT): 0=Locked, 1=Penalty, 2=Relational, 3=Flexible
- goodwill_score (INT): 0-100
- late_fee_rate (DECIMAL): e.g., 0.015 for 1.5%
- avg_latency_days (INT): For Monte Carlo

**obligations:**
- amount (DECIMAL): Negative=Payable, Positive=Receivable
- due_date (DATE)
- status (VARCHAR): 'PENDING', 'PAID', etc.

## Installation & Setup

### 1. Install Dependencies

```bash
cd backend
pip install fastapi uvicorn numpy pandas scipy psycopg2-binary python-dotenv
```

### 2. Configure Environment

Create `.env` file in project root:
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### 3. Run Tests

```bash
cd backend
python scripts/test_quant_engine.py
```

### 4. Start Server

```bash
cd backend
python main.py
```

Server runs on `http://localhost:8000`

## Testing Endpoints

### Test Dashboard Endpoint

```bash
curl http://localhost:8000/api/dashboard
```

### Test Decision Endpoint

```bash
curl http://localhost:8000/api/decision
```

### View API Documentation

Open browser: `http://localhost:8000/docs`

## Key Design Principles

1. **Deterministic:** All calculations are reproducible
2. **No AI/LLM:** Pure mathematical algorithms
3. **Database-Driven:** All data from Supabase via `get_db_connection()`
4. **Modular:** Each engine is independent and testable
5. **Type-Safe:** Uses type hints throughout
6. **Error-Handled:** Proper exception handling for DB failures

## Integration with Other Streams

- **Stream 1 (Ingestion):** Populates obligations table
- **Stream 3 (AI Agent):** Consumes quant outputs for decision-making
- **Frontend:** Displays dashboard metrics and optimization results

## Performance Considerations

- Entity lookup is O(1) using dictionary mapping
- Monte Carlo runs 1000 simulations by default (configurable)
- Linear programming uses scipy's 'highs' method (efficient)
- Database queries use indexes on status and due_date

## Troubleshooting

**Database Connection Failed:**
- Check DATABASE_URL in .env
- Verify Supabase credentials
- Ensure SSL mode is 'require'

**Optimization Infeasible:**
- Check if balance < sum(Tier 0 obligations)
- Verify late_fee_rate and goodwill_score are valid
- Review constraint formulation

**Monte Carlo Low Survival:**
- Indicates high risk of liquidity breach
- Review avg_latency_days for entities
- Consider increasing simulations for accuracy

## Future Enhancements

- [ ] Add time-series forecasting for receivables
- [ ] Implement multi-objective optimization
- [ ] Add sensitivity analysis for key parameters
- [ ] Support for currency conversion
- [ ] Real-time streaming calculations
