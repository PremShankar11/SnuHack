# Quant Engine Quick Start Guide

## Installation

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `cashpilot` root directory:

```env
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require
GEMINI_API_KEY=your_gemini_api_key_here
```

## Running the Server

### Start FastAPI Server

```bash
cd backend
python main.py
```

The server will start on `http://localhost:8000`

## Testing the Quant Engine

### Run Unit Tests

```bash
cd backend
python scripts/test_quant_engine.py
```

Expected output:
```
============================================================
QUANT ENGINE (STREAM 2) TEST SUITE
============================================================

=== Testing Runway Engine ===
Balance: $10000.0
Days to Zero: 15
Breach Date: 2026-04-09
✓ Runway engine test passed

=== Testing Phantom Balance ===
Balance: $10000.0
Locked Amount: $3000.0
Usable Cash: $7000.0
✓ Phantom balance test passed

=== Testing Monte Carlo Simulation ===
Balance: $10000.0
Survival Probability: 0.85
✓ Monte Carlo test passed

=== Testing LP Optimizer ===
Balance: $5000.0
Total Obligations: $6000.0

Optimization Results:
  IRS: FULL
    Pay Now: $2000.0
    Delay: $0.0
  Vendor A: PARTIAL
    Pay Now: $1875.0
    Delay: $625.0
  Vendor B: PARTIAL
    Pay Now: $1125.0
    Delay: $375.0

✓ Optimizer test passed

=== Testing Database Integration ===
Found 12 pending obligations in database
✓ Database integration test passed

============================================================
ALL TESTS COMPLETED
============================================================
```

## API Endpoints

### 1. Dashboard Endpoint

Get global financial state with runway metrics:

```bash
curl http://localhost:8000/api/dashboard
```

Response:
```json
{
  "global_state": {
    "plaid_balance": 12450.00,
    "phantom_usable_cash": 4100.00,
    "locked_tier_0_funds": 8350.00,
    "runway_metrics": {
      "days_to_zero": 8,
      "breach_date": "2026-04-02",
      "monte_carlo_survival_prob": 0.12
    }
  }
}
```

### 2. Decision Endpoint

Get optimization directive for payment decisions:

```bash
curl http://localhost:8000/api/decision
```

Response:
```json
{
  "solver_directive": {
    "breach_amount": -200.00,
    "optimization_result": [
      {
        "obligation_id": "uuid-here",
        "entity_name": "Acme Supplies",
        "math_decision": "PARTIAL",
        "pay_now_amount": 100.00,
        "delay_amount": 300.00,
        "requested_extension_days": 7
      }
    ]
  }
}
```

### 3. Interactive API Documentation

Open in browser:
```
http://localhost:8000/docs
```

This provides Swagger UI for testing all endpoints interactively.

## Architecture Overview

```
Quant Engine Flow:
┌─────────────────┐
│   Supabase DB   │
│  - companies    │
│  - entities     │
│  - obligations  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ quant_routes.py │ ◄── FastAPI Endpoints
│ fetch_data()    │
└────────┬────────┘
         │
         ├──► runway.py          (Days to Zero)
         ├──► phantom_balance.py (Usable Cash)
         ├──► monte_carlo.py     (Survival Probability)
         └──► optimizer.py       (Payment Decisions)
```

## Module Details

### Runway Engine
- **File:** `quant/runway.py`
- **Purpose:** Calculate days until cash runs out
- **Algorithm:** Deterministic balance simulation

### Phantom Balance
- **File:** `quant/phantom_balance.py`
- **Purpose:** Ring-fence Tier 0 obligations
- **Algorithm:** Sum locked amounts, subtract from balance

### Monte Carlo
- **File:** `quant/monte_carlo.py`
- **Purpose:** Probabilistic runway with delays
- **Algorithm:** 1000 simulations with N(0, σ) delays

### Optimizer
- **File:** `quant/optimizer.py`
- **Purpose:** Minimize late fees + goodwill penalties
- **Algorithm:** Linear programming (scipy.optimize.linprog)

## Troubleshooting

### Database Connection Error

```
🔥 Connection Error: could not connect to server
```

**Solution:**
- Verify DATABASE_URL in `.env`
- Check Supabase credentials
- Ensure `sslmode=require` is in connection string

### Import Error

```
ModuleNotFoundError: No module named 'numpy'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Port Already in Use

```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

## Integration with Frontend

The frontend can consume these endpoints:

```typescript
// Fetch dashboard data
const response = await fetch('http://localhost:8000/api/dashboard');
const data = await response.json();

console.log(data.global_state.runway_metrics.days_to_zero);
```

## Next Steps

1. ✅ Quant Engine is now operational
2. Integrate with AI Agent (Stream 3) for decision execution
3. Connect frontend to display metrics
4. Add real-time updates via WebSocket (optional)
5. Deploy to production environment

## Support

For issues or questions:
- Check `QUANT_ENGINE_README.md` for detailed documentation
- Review test output for specific module failures
- Verify database schema matches `schema.sql`
