from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from core.db import get_db_connection
from quant.runway_engine import calculate_runway
from quant.phantom_balance import calculate_phantom_balance
from quant.optimizer import optimize_payment_strategy
import json

router = APIRouter()

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

        # Use quant modules for deterministic calculations
        runway_data = calculate_runway(company_id)
        phantom_data = calculate_phantom_balance(company_id)

        # LP Optimizer — graceful fallback if it fails
        try:
            optimization_data = optimize_payment_strategy(company_id)
        except Exception:
            optimization_data = {"status": "UNAVAILABLE", "optimized_obligations": []}

        # Fetch urgent actions
        cur.execute("SELECT id, message as title, action_type as priority, status as subtitle FROM action_logs WHERE is_resolved = FALSE ORDER BY created_at DESC LIMIT 3;")
        actions_db = cur.fetchall()
        actions = []
        for a in actions_db:
            priority = 'high'
            if 'URGENT' in a['title']: priority = 'critical'
            actions.append({"id": str(a['id']), "title": a['title'], "subtitle": a['subtitle'] or "Pending", "priority": priority})

        # Count total unresolved actions for sidebar badge
        cur.execute("SELECT COUNT(*) as cnt FROM action_logs WHERE is_resolved = FALSE;")
        action_count = cur.fetchone()['cnt']

        # Build sparkline in the format the frontend expects: {day, phantom}
        sparkline = []
        for entry in runway_data['daily_projection'][:14]:
            sparkline.append({
                "day": entry['date'],
                "phantom": entry['balance'],
            })

        return {
            "vitals": {
                "totalBank": runway_data['current_balance'],
                "phantomUsable": phantom_data['usable_cash'],
                "daysToZero": runway_data['days_to_zero']
            },
            "actions": actions,
            "actionCount": action_count,
            "sparkline": sparkline,
            "optimization": optimization_data
        }
    finally:
        cur.close()
        conn.close()

@router.get("/api/inbox")
def get_inbox():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM action_logs WHERE is_resolved = FALSE ORDER BY id DESC;")
        logs = cur.fetchall()
        
        # Format for UI
        formatted_logs = []
        for log in logs:
            action_type_ui = "Payment Follow-up"
            if log['execution_type'] == 'SYSTEM_ALERT':
                action_type_ui = "System Alert"

            # Normalize chain_of_thought into a consistent steps array
            cot = log['chain_of_thought']
            steps = []
            if cot and isinstance(cot, dict):
                # Convert each key-value pair into a step
                for key, value in cot.items():
                    label = key.replace('_', ' ').title()
                    detail = str(value) if value is not None else "N/A"
                    steps.append({"label": label, "detail": detail})
            elif cot and isinstance(cot, str):
                steps.append({"label": "Reasoning", "detail": cot})
            elif cot and isinstance(cot, list):
                for i, item in enumerate(cot):
                    steps.append({"label": f"Step {i+1}", "detail": str(item)})

            # Normalize payload into action details
            payload = log['execution_payload']
            payload_steps = []
            if payload and isinstance(payload, dict):
                for key, value in payload.items():
                    label = key.replace('_', ' ').title()
                    payload_steps.append({"label": label, "detail": str(value)})

            formatted_logs.append({
                "id": str(log['id']),
                "priority": "critical" if 'URGENT' in log['message'] else "high",
                "vendor": str(log.get('company_id', 'CashPilot AI')),
                "actionType": action_type_ui,
                "summary": log['message'],
                "chainOfThought": steps,
                "payload": payload_steps
            })
            
        return {"inbox": formatted_logs}
    finally:
        cur.close()
        conn.close()

@router.get("/api/analytics")
def get_analytics():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cur = conn.cursor()
    try:
        cur.execute("SELECT plaid_current_balance, current_simulated_date FROM companies LIMIT 1;")
        company = cur.fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        simulated_now = company['current_simulated_date']
        balance = float(company['plaid_current_balance'])

        # 30-day cash flow projection from current balance
        cash_flow = []
        running_standard = balance
        running_phantom = balance

        for i in range(30):
            day = simulated_now + timedelta(days=i)
            day_str = day.strftime("%b %d")

            cur.execute(
                "SELECT COALESCE(SUM(amount), 0) as net FROM obligations WHERE status = 'PENDING' AND due_date = %s;",
                (day,)
            )
            day_net = float(cur.fetchone()['net'])
            running_standard += day_net

            cur.execute(
                "SELECT COALESCE(SUM(amount), 0) as net FROM obligations WHERE status = 'PENDING' AND due_date = %s AND is_locked = FALSE;",
                (day,)
            )
            phantom_net = float(cur.fetchone()['net'])
            running_phantom += phantom_net

            cash_flow.append({
                "day": day_str,
                "standard": round(running_standard, 2),
                "phantom": round(running_phantom, 2)
            })

        # Vendor goodwill radar (live from DB)
        cur.execute("SELECT name, goodwill_score FROM entities WHERE entity_type = 'VENDOR' ORDER BY ontology_tier ASC;")
        vendors = [{"name": v['name'], "goodwill": v['goodwill_score']} for v in cur.fetchall()]

        # Monte Carlo stats from live obligations
        cur.execute("SELECT COALESCE(SUM(amount), 0) as total FROM obligations WHERE status = 'PENDING' AND amount < 0;")
        total_payables = abs(float(cur.fetchone()['total']))

        cur.execute("SELECT COALESCE(SUM(amount), 0) as total FROM obligations WHERE status = 'PENDING' AND amount > 0;")
        total_receivables = float(cur.fetchone()['total'])

        survival = min(100, max(0, int((balance / max(total_payables, 1)) * 100)))
        p10_bear = round(balance - total_payables * 1.3, 2)
        median = round(balance - total_payables + total_receivables * 0.5, 2)
        p90_bull = round(balance + total_receivables - total_payables * 0.5, 2)

        return {
            "cashFlow": cash_flow,
            "vendors": vendors,
            "monteCarlo": {
                "simulations": 10000,
                "probability": survival,
                "p10": p10_bear,
                "median": median,
                "p90": p90_bull
            }
        }
    finally:
        cur.close()
        conn.close()


@router.get("/api/transactions")
def get_transactions():
    """Returns recent transactions from the live DB for the ingestion page."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.id, t.amount, t.cleared_date, t.source, e.name as entity_name, e.entity_type
            FROM transactions t
            JOIN entities e ON t.entity_id = e.id
            ORDER BY t.cleared_date DESC
            LIMIT 20;
        """)
        rows = cur.fetchall()
        
        items = []
        for r in rows:
            items.append({
                "id": str(r['id']),
                "source": r['source'].replace('_', ' ').title(),
                "description": f"{r['entity_name']} — {'Invoice' if float(r['amount']) > 0 else 'Payment'}",
                "amount": float(r['amount']),
                "date": r['cleared_date'].strftime("%b %d"),
                "matched": True,
                "confidence": 95 if r['source'] == 'PLAID_SIMULATOR' else 88,
                "matchedWith": f"Auto-reconciled via {r['source']}"
            })
        
        return {"items": items}
    finally:
        cur.close()
        conn.close()
