# CashPilot Quick Start Guide

## Prerequisites
- Python 3.9+
- Node.js 18+
- Supabase account (or PostgreSQL database)
- Gemini API key (for receipt OCR)

## 1. Database Setup

### Option A: Supabase (Recommended)
1. Create account at https://supabase.com
2. Create new project
3. Go to SQL Editor
4. Run the contents of `schema.sql`
5. Copy your project URL and anon key

### Option B: Local PostgreSQL
```bash
# Install PostgreSQL
# Create database
createdb cashpilot

# Run schema
psql cashpilot < schema.sql
```

## 2. Backend Setup

```bash
cd cashpilot/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment
Create `cashpilot/.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
GEMINI_API_KEY=your-gemini-api-key
```

### Seed Database
```bash
# Seed initial data
python scripts/seed_data.py

# Generate simulated transactions
python scripts/plaid_simulator.py
```

### Start Backend
```bash
python main.py
```

Backend will run on http://localhost:8000

## 3. Frontend Setup

```bash
cd cashpilot

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on http://localhost:3000

## 4. Verify Installation

### Test Backend
```bash
cd backend
python scripts/test_integration.py
```

You should see:
```
✅ Dashboard endpoint working
✅ Decision endpoint working
✅ Analytics endpoint working
✅ Inbox endpoint working
✅ Transactions endpoint working
✅ Simulation advance working
✅ Contract compliance verified

🎉 All tests passed!
```

### Test Frontend
1. Open http://localhost:3000
2. You should see the dashboard with:
   - Total Bank Balance
   - Phantom Usable Cash
   - Days to Zero (Runway)
   - 14-day cashflow chart
   - Monte Carlo survival probability

## 5. Try Key Features

### Simulation Time Travel
1. Use the slider at the top to advance time
2. Watch obligations resolve and new ones appear
3. See balance and runway update in real-time

### Receipt Upload
1. Go to "Ingestion" page
2. Drag and drop a receipt image (or click to browse)
3. Watch Gemini Vision OCR extract data
4. See automatic reconciliation in the ledger

### Analytics & Optimization
1. Go to "Analytics" page
2. View 30-day cashflow projection
3. See vendor goodwill radar chart
4. Review LP optimizer payment decisions

### Action Inbox
1. Go to "Inbox" page
2. See AI-generated action items
3. Click to view chain-of-thought reasoning
4. Review email drafts and approve/reject

## 6. Understanding the Data Flow

```
1. Plaid Simulator → Generates bank transactions
2. Receipt OCR → Extracts vendor invoices
3. N-Way Reconciliation → Merges duplicates
4. Quant Engine → Calculates runway, phantom balance, Monte Carlo
5. LP Optimizer → Determines optimal payment strategy
6. Action Logs → AI generates intervention recommendations
7. Frontend → Displays everything in real-time
```

## Common Issues

### "Database connection failed"
- Check SUPABASE_URL and SUPABASE_KEY in .env
- Verify Supabase project is active
- Test connection: `python scripts/check_db.py`

### "No data showing"
- Run seed scripts: `python scripts/seed_data.py`
- Run simulator: `python scripts/plaid_simulator.py`
- Check database: `python scripts/check_db.py`

### "Gemini API error"
- Verify GEMINI_API_KEY is set in .env
- Check API key is valid at https://aistudio.google.com/apikey
- Receipt OCR requires valid key

### "Port already in use"
- Backend: Change port in main.py (default 8000)
- Frontend: Change port with `npm run dev -- -p 3001`

## Next Steps

1. Read `INTEGRATION_COMPLETE.md` for detailed architecture
2. Review `backend/ARCHITECTURE.md` for backend design
3. Check `backend/QUANT_ENGINE_README.md` for math details
4. Explore `shared_contracts.json` for API schemas
5. Run `python scripts/demo_quant_api.py` for API examples

## Development Workflow

### Making Changes

**Backend:**
1. Edit files in `backend/`
2. Backend auto-reloads (uvicorn --reload)
3. Test with `python scripts/test_integration.py`

**Frontend:**
1. Edit files in `app/`
2. Next.js auto-reloads
3. Check browser console for errors

**Database:**
1. Make schema changes in Supabase SQL editor
2. Update `schema.sql`
3. Re-run seed scripts if needed

### Testing

```bash
# Backend API tests
cd backend
python scripts/test_backend_api.py
python scripts/test_quant_engine.py
python scripts/test_integration.py

# Full flow test
python scripts/test_full_flow.py

# Scenario tests
python scripts/test_scenarios.py
```

## Production Deployment

### Backend (FastAPI)
- Deploy to: Railway, Render, Fly.io, or AWS Lambda
- Set environment variables
- Use production ASGI server (gunicorn + uvicorn)

### Frontend (Next.js)
- Deploy to: Vercel, Netlify, or AWS Amplify
- Set NEXT_PUBLIC_API_URL to production backend URL
- Build: `npm run build`

### Database
- Use Supabase production tier
- Enable connection pooling
- Set up backups and monitoring

## Support

Need help? Check:
1. This guide
2. `INTEGRATION_COMPLETE.md`
3. Backend logs in terminal
4. Browser console (F12)
5. Supabase logs in dashboard

---

**Ready to go!** 🚀

Start backend: `cd backend && python main.py`
Start frontend: `cd .. && npm run dev`
Open: http://localhost:3000
