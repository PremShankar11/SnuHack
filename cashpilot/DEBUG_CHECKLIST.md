# CashPilot Debug Checklist

Use this checklist to systematically debug issues in the CashPilot application.

## Backend Issues

### ✅ Backend Won't Start

**Symptoms:**
- `python main.py` fails
- Import errors
- Database connection errors

**Debug Steps:**
1. Check Python version: `python --version` (need 3.9+)
2. Verify virtual environment is activated: `which python` should show venv path
3. Install dependencies: `pip install -r requirements.txt`
4. Check .env file exists in `cashpilot/` directory
5. Verify environment variables:
   ```python
   import os
   print(os.environ.get('SUPABASE_URL'))
   print(os.environ.get('SUPABASE_KEY'))
   ```
6. Test database connection: `python scripts/check_db.py`
7. Check port 8000 is available: `netstat -an | grep 8000`

**Common Fixes:**
- Missing .env file → Create it with correct credentials
- Wrong Python version → Use pyenv or conda to install 3.9+
- Port in use → Kill process or change port in main.py
- Missing dependencies → Run `pip install -r requirements.txt`

### ✅ API Endpoints Return 500 Errors

**Symptoms:**
- `/quant/api/dashboard` returns 500
- `/quant/api/decision` returns 500
- Backend logs show exceptions

**Debug Steps:**
1. Check backend terminal for stack traces
2. Verify database has data: `python scripts/check_db.py`
3. Test individual quant modules:
   ```bash
   python scripts/test_quant_engine.py
   ```
4. Check obligations table has pending items:
   ```sql
   SELECT COUNT(*) FROM obligations WHERE status = 'PENDING';
   ```
5. Verify entities table has vendors:
   ```sql
   SELECT COUNT(*) FROM entities WHERE entity_type = 'VENDOR';
   ```

**Common Fixes:**
- Empty database → Run `python scripts/seed_data.py`
- No pending obligations → Run `python scripts/plaid_simulator.py`
- Date format issues → Check obligations.due_date is DATE type
- Missing entity data → Re-run seed script

### ✅ Quant Calculations Seem Wrong

**Symptoms:**
- Days to zero is always 999
- Phantom balance equals total balance
- Monte Carlo shows 100% or 0% survival

**Debug Steps:**
1. Check obligation amounts and due dates:
   ```sql
   SELECT * FROM obligations WHERE status = 'PENDING' ORDER BY due_date LIMIT 10;
   ```
2. Verify entity ontology tiers:
   ```sql
   SELECT name, ontology_tier FROM entities;
   ```
3. Test runway calculation:
   ```python
   from quant.runway import calculate_runway
   balance = 10000
   obligations = [{'amount': -5000, 'due_date': '2026-03-30'}]
   print(calculate_runway(balance, obligations))
   ```
4. Check for date type mismatches in code

**Common Fixes:**
- All obligations in past → Advance simulation or create future obligations
- No Tier 0 entities → Update entities table with ontology_tier = 0 for taxes
- Negative balance → Seed more realistic starting balance
- Date strings not parsing → Ensure ISO format YYYY-MM-DD

### ✅ Receipt OCR Not Working

**Symptoms:**
- `/api/ingest/receipt` returns 400 or 500
- "GEMINI_API_KEY is not set" error
- Gemini API errors

**Debug Steps:**
1. Check GEMINI_API_KEY in .env: `echo $GEMINI_API_KEY`
2. Verify API key is valid at https://aistudio.google.com/apikey
3. Test Gemini directly:
   ```python
   import google.generativeai as genai
   genai.configure(api_key='your-key')
   model = genai.GenerativeModel('gemini-2.5-flash')
   response = model.generate_content("Hello")
   print(response.text)
   ```
4. Check image file format (JPEG, PNG supported)
5. Verify file size < 10MB

**Common Fixes:**
- Missing API key → Add to .env file
- Invalid API key → Generate new one from Google AI Studio
- Wrong model name → Use 'gemini-2.5-flash' or 'gemini-1.5-pro'
- Image too large → Resize before upload

## Frontend Issues

### ✅ Frontend Shows "Network Error"

**Symptoms:**
- Dashboard shows error message
- Browser console shows fetch errors
- "Failed to fetch" errors

**Debug Steps:**
1. Verify backend is running: `curl http://localhost:8000/`
2. Check NEXT_PUBLIC_API_URL in .env.local
3. Open browser DevTools (F12) → Network tab
4. Look for failed requests (red)
5. Check CORS errors in console
6. Verify API_URL import in components:
   ```typescript
   import { API_URL } from './lib/api';
   console.log('API_URL:', API_URL);
   ```

**Common Fixes:**
- Backend not running → Start with `python main.py`
- Wrong API URL → Update .env.local with correct URL
- CORS error → Verify CORSMiddleware in main.py allows origin
- Port mismatch → Ensure backend on 8000, frontend on 3000

### ✅ No Data Showing on Dashboard

**Symptoms:**
- Dashboard loads but shows $0 everywhere
- Charts are empty
- "Loading..." never finishes

**Debug Steps:**
1. Check browser console for errors
2. Verify API response in Network tab:
   - Look for `/quant/api/dashboard` request
   - Check response status (should be 200)
   - Inspect response JSON
3. Test API directly: `curl http://localhost:8000/quant/api/dashboard`
4. Check database has data: `python scripts/check_db.py`
5. Verify refreshKey is updating in SimulationContext

**Common Fixes:**
- Empty database → Run seed scripts
- API returning empty data → Check backend logs
- Frontend not parsing response → Check data transformation in page.tsx
- Stale data → Hard refresh browser (Ctrl+Shift+R)

### ✅ Simulation Slider Not Working

**Symptoms:**
- Moving slider does nothing
- Data doesn't update after simulation
- Simulation date doesn't change

**Debug Steps:**
1. Check browser console for errors
2. Verify `/api/simulate/advance` endpoint works:
   ```bash
   curl -X POST http://localhost:8000/api/simulate/advance \
     -H "Content-Type: application/json" \
     -d '{"days_offset": 5}'
   ```
3. Check SimulationContext state updates:
   ```typescript
   console.log('daysOffset:', daysOffset);
   console.log('refreshKey:', refreshKey);
   ```
4. Verify useEffect dependencies include refreshKey
5. Check for concurrent simulation requests

**Common Fixes:**
- Simulation endpoint failing → Check backend logs
- refreshKey not triggering re-fetch → Add to useEffect deps
- Concurrent requests → Add request deduplication
- Database not updating → Check simulation_router.py logic

### ✅ Analytics Page Shows Wrong Data

**Symptoms:**
- Cashflow chart shows flat line
- Vendor radar is empty
- LP optimizer results missing

**Debug Steps:**
1. Check all three API calls in useEffect:
   - `/api/analytics`
   - `/quant/api/decision`
   - `/quant/api/dashboard`
2. Verify each response in Network tab
3. Check for null/undefined data:
   ```typescript
   console.log('data:', data);
   console.log('decisionData:', decisionData);
   console.log('dashboardData:', dashboardData);
   ```
4. Verify conditional rendering logic
5. Check for missing null checks

**Common Fixes:**
- Missing null checks → Add `?.` optional chaining
- Wrong data structure → Check API response matches expected format
- Loading state issues → Ensure loading=false after all fetches
- Empty optimization results → Check if breach detected

### ✅ Receipt Upload Not Working

**Symptoms:**
- Drag and drop does nothing
- Upload button doesn't work
- "Scanning..." never finishes

**Debug Steps:**
1. Check file input ref is connected
2. Verify file type is image: `console.log(file.type)`
3. Check FormData is created correctly
4. Inspect `/api/ingest/receipt` request in Network tab
5. Check backend logs for OCR errors
6. Verify GEMINI_API_KEY is set

**Common Fixes:**
- File input not triggering → Check ref and onClick handler
- Wrong file type → Add accept="image/*" to input
- Backend OCR failing → Check Gemini API key
- Large file timeout → Reduce image size or increase timeout

## Database Issues

### ✅ Database Connection Fails

**Symptoms:**
- "Database connection failed" errors
- psycopg2 connection errors
- Timeout errors

**Debug Steps:**
1. Test connection manually:
   ```python
   from core.db import get_db_connection
   conn = get_db_connection()
   print("Connected!" if conn else "Failed")
   ```
2. Verify Supabase project is active
3. Check connection string format
4. Test with psql: `psql $SUPABASE_URL`
5. Check firewall/network settings

**Common Fixes:**
- Wrong credentials → Update .env with correct URL/key
- Supabase project paused → Unpause in dashboard
- Network issue → Check VPN or firewall
- Connection pooling → Add pooling config to Supabase

### ✅ Schema Errors

**Symptoms:**
- "relation does not exist" errors
- "column does not exist" errors
- Foreign key constraint violations

**Debug Steps:**
1. Verify schema is applied: Check tables in Supabase dashboard
2. Run schema.sql again if needed
3. Check table names match code (case-sensitive)
4. Verify column names and types
5. Check foreign key relationships

**Common Fixes:**
- Missing tables → Run schema.sql in SQL editor
- Wrong column names → Update code or schema
- Constraint violations → Check data integrity
- Type mismatches → Ensure DATE vs TIMESTAMP consistency

### ✅ Data Integrity Issues

**Symptoms:**
- Orphaned obligations (no entity)
- Negative goodwill scores
- Future dates in past
- Duplicate obligations

**Debug Steps:**
1. Check for orphaned records:
   ```sql
   SELECT * FROM obligations WHERE entity_id NOT IN (SELECT id FROM entities);
   ```
2. Verify goodwill scores in range:
   ```sql
   SELECT * FROM entities WHERE goodwill_score < 0 OR goodwill_score > 100;
   ```
3. Check date consistency:
   ```sql
   SELECT * FROM obligations WHERE due_date < CURRENT_DATE AND status = 'PENDING';
   ```
4. Find duplicates:
   ```sql
   SELECT entity_id, amount, due_date, COUNT(*) 
   FROM obligations 
   GROUP BY entity_id, amount, due_date 
   HAVING COUNT(*) > 1;
   ```

**Common Fixes:**
- Orphaned records → Delete or fix foreign keys
- Invalid scores → Update with LEAST/GREATEST constraints
- Old pending obligations → Mark as PAID or delete
- Duplicates → Run reconciliation or delete extras

## Performance Issues

### ✅ Slow API Responses

**Symptoms:**
- Dashboard takes >2 seconds to load
- Simulation advance is slow
- Monte Carlo timeout

**Debug Steps:**
1. Check database query performance
2. Add indexes to frequently queried columns:
   ```sql
   CREATE INDEX idx_obligations_status ON obligations(status);
   CREATE INDEX idx_obligations_due_date ON obligations(due_date);
   ```
3. Profile Python code with cProfile
4. Check Monte Carlo simulation count (reduce if needed)
5. Monitor database connection pool

**Common Fixes:**
- Missing indexes → Add to frequently queried columns
- Too many simulations → Reduce from 1000 to 100
- Large result sets → Add pagination
- Slow queries → Optimize with EXPLAIN ANALYZE

### ✅ High Memory Usage

**Symptoms:**
- Backend crashes with OOM
- Frontend tab crashes
- Slow rendering

**Debug Steps:**
1. Check obligation count: `SELECT COUNT(*) FROM obligations;`
2. Monitor memory with `top` or Task Manager
3. Profile with memory_profiler
4. Check for memory leaks in loops
5. Verify database connections are closed

**Common Fixes:**
- Too many obligations → Archive old ones
- Memory leak → Close cursors and connections
- Large arrays → Use pagination or streaming
- Frontend re-renders → Use React.memo and useMemo

## Integration Issues

### ✅ Frontend and Backend Out of Sync

**Symptoms:**
- Frontend expects different data structure
- API contract violations
- TypeScript errors

**Debug Steps:**
1. Compare API response to shared_contracts.json
2. Check frontend data transformation logic
3. Verify all required fields are present
4. Test with Postman or curl
5. Check for version mismatches

**Common Fixes:**
- Update frontend to match backend response
- Update backend to match contract
- Add data transformation layer
- Version API endpoints

### ✅ Simulation State Inconsistency

**Symptoms:**
- Different pages show different dates
- Balance doesn't match across pages
- Stale data after simulation

**Debug Steps:**
1. Check SimulationContext refreshKey updates
2. Verify all pages use refreshKey in useEffect
3. Check for cached responses
4. Verify database updates in simulation_router.py
5. Test with browser DevTools → Application → Clear storage

**Common Fixes:**
- Add refreshKey to all useEffect dependencies
- Clear browser cache
- Add cache-control headers to API responses
- Ensure database commits in simulation

## Testing

### ✅ Run All Tests

```bash
# Backend tests
cd backend
python scripts/test_integration.py
python scripts/test_backend_api.py
python scripts/test_quant_engine.py
python scripts/test_full_flow.py

# Manual frontend test
# 1. Open http://localhost:3000
# 2. Check all pages load
# 3. Try simulation slider
# 4. Upload receipt
# 5. Check analytics
```

### ✅ Verify Contracts

```bash
# Check API responses match shared_contracts.json
curl http://localhost:8000/quant/api/dashboard | jq .
curl http://localhost:8000/quant/api/decision | jq .
```

## Quick Fixes

### Reset Everything
```bash
# Backend
cd backend
python scripts/seed_data.py
python scripts/plaid_simulator.py

# Frontend
rm -rf .next
npm run dev
```

### Fresh Start
```bash
# Stop all processes
# Delete database tables and re-run schema.sql
# Delete venv and reinstall
# Delete node_modules and reinstall
# Clear browser cache
# Start fresh
```

---

**Still stuck?** Check:
1. Backend terminal logs
2. Browser console (F12)
3. Network tab in DevTools
4. Supabase logs
5. INTEGRATION_COMPLETE.md for architecture details
