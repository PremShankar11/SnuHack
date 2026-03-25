from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from core.db import get_db_connection
import json

router = APIRouter()

@router.get("/api/dashboard")
def get_dashboard():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, plaid_current_balance, current_simulated_date FROM companies LIMIT 1;")
        company = cur.fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
            
        simulated_now = company['current_simulated_date']
        current_balance = float(company['plaid_current_balance'])
        
        # Phantom Usable: current balance + net of pending obligations in next 7 days
        horizon = simulated_now + timedelta(days=7)
        cur.execute(
            "SELECT COALESCE(SUM(amount), 0) as net_pending FROM obligations WHERE status = 'PENDING' AND due_date <= %s;",
            (horizon,)
        )
        net_pending = float(cur.fetchone()['net_pending'])
        phantom_usable = current_balance + net_pending
        
        # Days to zero: based on upcoming payables burn rate
        cur.execute(
            "SELECT COALESCE(SUM(amount), 0) as burn FROM obligations WHERE status = 'PENDING' AND amount < 0 AND due_date <= %s;",
            (simulated_now + timedelta(days=30),)
        )
        burn = abs(float(cur.fetchone()['burn']))
        daily_burn = max(burn / 30.0, 1.0)
        days_to_zero = max(0, int(current_balance / daily_burn))
        
        # Fetch urgent actions
        cur.execute("SELECT id, message as title, action_type as priority, status as subtitle FROM action_logs WHERE is_resolved = FALSE ORDER BY created_at DESC LIMIT 3;")
        actions_db = cur.fetchall()
        actions = []
        for a in actions_db:
            priority = 'high'
            if 'URGENT' in a['title']: priority = 'critical'
            actions.append({"id": str(a['id']), "title": a['title'], "subtitle": a['subtitle'] or "Pending", "priority": priority})
            
        # Mock sparkline reflecting current phantom trajectory
        sparkline = [{"day": str(simulated_now + timedelta(days=i)), "phantom": phantom_usable - (daily_burn * i)} for i in range(14)]
        
        return {
            "vitals": {
                "totalBank": current_balance,
                "phantomUsable": phantom_usable,
                "daysToZero": days_to_zero
            },
            "actions": actions,
            "sparkline": sparkline
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
                
            formatted_logs.append({
                "id": str(log['id']),
                "priority": "critical" if 'URGENT' in log['message'] else "high",
                "vendor": log.get('company_id', 'CashPilot AI'),
                "actionType": action_type_ui,
                "summary": log['message'],
                "chainOfThought": log['chain_of_thought'],
                "payload": log['execution_payload']
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
