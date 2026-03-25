from fastapi import APIRouter, HTTPException
from datetime import timedelta
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
        # Get actual simulated date & balance
        cur.execute("SELECT id, plaid_current_balance, current_simulated_date FROM companies LIMIT 1;")
        company = cur.fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
            
        simulated_now = company['current_simulated_date']
        current_balance = float(company['plaid_current_balance'])
        
        # Calculate Phantom Usable (balance + net pending in next 7 days)
        horizon = simulated_now + timedelta(days=7)
        cur.execute("SELECT SUM(amount) as net_pending FROM obligations WHERE status = 'PENDING' AND due_date <= %s;", (horizon,))
        row = cur.fetchone()
        net_pending = float(row['net_pending']) if row and row['net_pending'] else 0.0
        phantom_usable = current_balance + net_pending
        
        # Calculate daysToZero simple heuristic (burn rate based on next 30 days of payables)
        cur.execute("SELECT SUM(amount) as burn FROM obligations WHERE status = 'PENDING' AND amount < 0 AND due_date <= %s;", (simulated_now + timedelta(days=30),))
        burn_row = cur.fetchone()
        burn = abs(float(burn_row['burn'])) if burn_row and burn_row['burn'] else 1.0
        daily_burn = max(burn / 30.0, 1.0)
        days_to_zero = int(current_balance / daily_burn)
        
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
