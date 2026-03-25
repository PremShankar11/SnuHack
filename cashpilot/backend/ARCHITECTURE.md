# CashPilot Backend Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CASHPILOT BACKEND                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   STREAM 1      │     │   STREAM 2      │     │   STREAM 3      │
│   Perception    │────▶│   Quant Engine  │────▶│   AI Agent      │
│   Layer         │     │   (Deterministic)│     │   (Execution)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                        │
        │                       │                        │
        ▼                       ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SUPABASE POSTGRESQL                         │
│  companies | entities | transactions | obligations | action_logs │
└─────────────────────────────────────────────────────────────────┘
```

## Stream 1: Perception Layer

**Purpose:** Data ingestion and reconciliation

```
Receipt Image
     │
     ▼
┌─────────────────────┐
│  Gemini 1.5 Pro     │  Vision OCR
│  Vision API         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  N-Way              │  String Similarity (rapidfuzz)
│  Reconciliation     │  Amount Matching
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Database Update    │  Merge or Create Obligation
└─────────────────────┘
```

**Files:**
- `services/ingestion_pipeline.py`
- `api/router.py`

**Endpoints:**
- `POST /api/ingest/receipt`

## Stream 2: Quant Engine (THIS IMPLEMENTATION)

**Purpose:** Deterministic financial calculations

```
Database Query
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    fetch_financial_data()                        │
│  - Current balance                                               │
│  - Pending obligations                                           │
│  - Entity metadata (tier, goodwill, late_fee_rate, latency)     │
└──────────────────────────┬───────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Runway   │   │ Phantom  │   │ Monte    │
    │ Engine   │   │ Balance  │   │ Carlo    │
    └──────────┘   └──────────┘   └──────────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                           ▼
                    ┌──────────┐
                    │ LP       │
                    │Optimizer │
                    └──────────┘
                           │
                           ▼
                    API Response
```

**Modules:**

### 1. Runway Engine (`quant/runway.py`)
```python
calculate_runway(balance, obligations)
→ {days_to_zero, breach_date}
```
- Sorts obligations by due_date
- Simulates daily balance trajectory
- Detects first negative balance

### 2. Phantom Balance (`quant/phantom_balance.py`)
```python
calculate_usable_cash(balance, obligations, entities)
→ {usable_cash, locked_amount}
```
- Identifies Tier 0 entities (critical)
- Locks their obligation amounts
- Returns remaining usable cash

### 3. Monte Carlo (`quant/monte_carlo.py`)
```python
monte_carlo_simulation(balance, obligations, entities, n=1000)
→ {survival_probability}
```
- Runs N simulations
- Applies random delays: N(0, avg_latency_days)
- Counts survival rate

### 4. LP Optimizer (`quant/optimizer.py`)
```python
optimize_payments(balance, obligations, entities)
→ {optimization_result[]}
```
- Objective: Minimize late_fees + goodwill_penalties
- Constraints:
  - sum(payments) ≤ balance
  - Tier 0 must be fully paid
  - Others: 0 ≤ fraction ≤ 1
- Uses scipy.optimize.linprog

**Files:**
- `quant/runway.py`
- `quant/phantom_balance.py`
- `quant/monte_carlo.py`
- `quant/optimizer.py`
- `api/quant_routes.py`

**Endpoints:**
- `GET /api/dashboard` → Global state + runway metrics
- `GET /api/decision` → Optimization directive

## Stream 3: AI Agent (Future)

**Purpose:** Autonomous execution of financial decisions

```
Quant Engine Output
     │
     ▼
┌─────────────────────┐
│  Claude AI Agent    │  Chain-of-Thought Reasoning
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Action Generation  │  Email drafts, API calls
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Execution Layer    │  Gmail, Stripe, Shopify
└─────────────────────┘
```

**Status:** Not yet implemented

## Database Schema

```sql
companies
├── id (UUID)
├── plaid_current_balance (DECIMAL)
└── current_simulated_date (DATE)

entities
├── id (UUID)
├── company_id (UUID FK)
├── name (VARCHAR)
├── entity_type (VARCHAR) -- 'VENDOR' | 'CLIENT'
├── ontology_tier (INT)   -- 0=Locked, 1=Penalty, 2=Relational, 3=Flexible
├── goodwill_score (INT)  -- 0-100
├── late_fee_rate (DECIMAL)
└── avg_latency_days (INT)

obligations
├── id (UUID)
├── entity_id (UUID FK)
├── amount (DECIMAL)      -- Negative=Payable, Positive=Receivable
├── due_date (DATE)
├── status (VARCHAR)      -- 'PENDING' | 'PAID' | 'SHUFFLED'
└── is_locked (BOOLEAN)

transactions
├── id (UUID)
├── entity_id (UUID FK)
├── amount (DECIMAL)
├── cleared_date (DATE)
└── source (VARCHAR)

action_logs
├── id (UUID)
├── obligation_id (UUID FK)
├── status (VARCHAR)
├── chain_of_thought (JSONB)
├── execution_type (VARCHAR)
├── execution_payload (JSONB)
└── agent_thread_id (VARCHAR)
```

## Data Flow

### Dashboard Request Flow

```
1. Frontend → GET /api/dashboard
2. quant_routes.fetch_financial_data()
   ├─ Query companies table → balance
   ├─ Query obligations table → pending obligations
   └─ Query entities table → entity metadata
3. Parallel execution:
   ├─ runway.calculate_runway()
   ├─ phantom_balance.calculate_usable_cash()
   └─ monte_carlo.monte_carlo_simulation()
4. Aggregate results
5. Return JSON response
```

### Decision Request Flow

```
1. Frontend → GET /api/decision
2. quant_routes.fetch_financial_data()
3. runway.calculate_runway() → detect breach
4. optimizer.optimize_payments()
   ├─ Build cost vector (late_fees + goodwill_penalties)
   ├─ Define constraints (balance limit, Tier 0 locks)
   ├─ Solve LP problem (scipy.linprog)
   └─ Format decisions (FULL | PARTIAL | DELAY)
5. Return optimization directive
```

## Technology Stack

### Core Framework
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### Database
- **PostgreSQL** (Supabase)
- **psycopg2** - Database adapter
- **RealDictCursor** - Dict-based results

### Scientific Computing
- **NumPy** - Numerical operations
- **Pandas** - Data manipulation
- **SciPy** - Linear programming (linprog)

### AI/ML (Stream 1)
- **Google Generative AI** - Gemini Vision OCR
- **rapidfuzz** - String similarity matching

### Utilities
- **python-dotenv** - Environment management
- **python-multipart** - File upload handling

## Design Principles

### 1. Deterministic Calculations
- No randomness in core logic (except Monte Carlo)
- Reproducible results for same inputs
- No AI/LLM in Quant Engine

### 2. Modular Architecture
- Each engine is independent
- Clear separation of concerns
- Easy to test and maintain

### 3. Database-Driven
- Single source of truth (Supabase)
- All data via `get_db_connection()`
- No hardcoded values

### 4. Type Safety
- Type hints throughout
- Pydantic models for validation
- Clear function signatures

### 5. Error Handling
- Graceful DB failure handling
- Fallback algorithms in optimizer
- Informative error messages

## Performance Characteristics

### Runway Engine
- **Time Complexity:** O(n log n) - sorting obligations
- **Space Complexity:** O(n)
- **Typical Runtime:** <10ms for 100 obligations

### Phantom Balance
- **Time Complexity:** O(n) - single pass through obligations
- **Space Complexity:** O(1)
- **Typical Runtime:** <5ms

### Monte Carlo
- **Time Complexity:** O(n × m) - n=obligations, m=simulations
- **Space Complexity:** O(n × m)
- **Typical Runtime:** ~100ms for 1000 simulations

### LP Optimizer
- **Time Complexity:** O(n³) - worst case for simplex
- **Space Complexity:** O(n²)
- **Typical Runtime:** ~50ms for 50 obligations

## Deployment Considerations

### Environment Variables
```env
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
GEMINI_API_KEY=your_api_key_here
```

### Server Configuration
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### CORS Settings
- Currently allows all origins (`*`)
- Restrict in production to frontend domain

### Database Connection
- Connection pooling recommended for production
- Timeout set to 10 seconds
- SSL mode required for Supabase

## Testing Strategy

### Unit Tests
- Test each engine independently
- Mock database connections
- Verify mathematical correctness

### Integration Tests
- Test API endpoints end-to-end
- Use test database
- Verify JSON contract compliance

### Performance Tests
- Benchmark each engine
- Test with large datasets (1000+ obligations)
- Monitor memory usage

## Future Enhancements

### Short Term
- [ ] Add caching for frequently accessed data
- [ ] Implement WebSocket for real-time updates
- [ ] Add request rate limiting
- [ ] Improve error logging

### Medium Term
- [ ] Multi-currency support
- [ ] Time-series forecasting
- [ ] Sensitivity analysis
- [ ] Historical trend analysis

### Long Term
- [ ] Machine learning for payment prediction
- [ ] Advanced optimization algorithms
- [ ] Real-time streaming calculations
- [ ] Multi-company support

## Monitoring & Observability

### Metrics to Track
- API response times
- Database query performance
- Monte Carlo simulation duration
- Optimization solver success rate
- Error rates by endpoint

### Logging
- Structured JSON logs
- Request/response logging
- Database query logging
- Error stack traces

### Health Checks
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": check_db_connection(),
        "timestamp": datetime.now().isoformat()
    }
```

## Security Considerations

### Database
- Use parameterized queries (prevents SQL injection)
- SSL/TLS for connections
- Least privilege access

### API
- Input validation via Pydantic
- CORS restrictions in production
- Rate limiting recommended

### Secrets
- Never commit .env files
- Use environment variables
- Rotate API keys regularly

## Support & Documentation

- **Quick Start:** `QUICKSTART_QUANT.md`
- **Full Documentation:** `QUANT_ENGINE_README.md`
- **API Docs:** `http://localhost:8000/docs`
- **Test Suite:** `scripts/test_quant_engine.py`
- **Demo Script:** `scripts/demo_quant_api.py`
