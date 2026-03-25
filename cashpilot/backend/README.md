# CashPilot - Backend

This folder contains the backend services for the CashPilot AI-driven financial autopilot. This implementation covers:
- **Stream 1: The Perception Layer** (Data Ingestion)
- **Stream 2: The Quant Engine** (Deterministic Financial Calculations)

## Requirements

Ensure you have Python 3.9+ installed. It is recommended to use a virtual environment.

```bash
cd backend
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

### Dependencies
Install all required packages:

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install fastapi uvicorn python-multipart psycopg2-binary rapidfuzz google-generativeai python-dotenv numpy pandas scipy
```

## Setup & Configuration

1. Make sure your `.env` file is located at the **root** of the monorepo (`../.env` relative to this folder).
2. The `.env` file must contain:
   ```env
   DATABASE_URL=postgresql://postgres:user@host:5432/postgres
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Running the Data Scripts

We have provided simulation scripts to populate the database and simulate background transactions.

To run the full suite (Seed Data, Simulate Plaid Transactions, and Vendor Goodwill Scoring):
```bash
# Ensure you are in the backend directory
python -m scripts.run_all
```

Alternatively, you can run them individually:
- `python -m scripts.seed_data`
- `python -m scripts.plaid_simulator`
- `python -m scripts.goodwill_scorer`

## Running the API Server

To start the FastAPI server, run:
```bash
# Ensure you are in the backend directory
uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).
Swagger UI Documentation will be at [http://localhost:8000/docs](http://localhost:8000/docs).

## Available Endpoints

### Stream 1: Perception Layer

#### `POST /api/ingest/receipt`
Accepts a multipart form data upload of a receipt image.
- **Workflow:** Passes the image to `gemini-1.5-pro` for strict JSON extraction matching the `ingestion_event` schema.
- Uses `rapidfuzz` to evaluate supplier name (String similarity > 80%) AND matches the exact `amount`.
- If match: Merges record into pending `obligations` and creates a `transaction`.
- If not matched: Creates a new pending `obligation`.

### Stream 2: Quant Engine

#### `GET /api/dashboard`
Returns global financial state with runway metrics.
- **Runway Engine:** Calculates days until cash runs out
- **Phantom Balance:** Ring-fences Tier 0 obligations
- **Monte Carlo:** Probabilistic survival analysis (1000 simulations)

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

#### `GET /api/decision`
Returns optimization directive for payment decisions.
- **LP Optimizer:** Minimizes late fees + goodwill penalties
- **Constraints:** Tier 0 must be paid, others can be fractional
- **Algorithm:** scipy.optimize.linprog

Response:
```json
{
  "solver_directive": {
    "breach_amount": -200.00,
    "optimization_result": [
      {
        "obligation_id": "uuid",
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

## Quant Engine Documentation

For detailed documentation on the Quant Engine (Stream 2):
- **Full Documentation:** See `QUANT_ENGINE_README.md`
- **Quick Start Guide:** See `QUICKSTART_QUANT.md`

### Testing Quant Engine

Run unit tests:
```bash
python scripts/test_quant_engine.py
```

Test API endpoints (requires server running):
```bash
python scripts/demo_quant_api.py
```
