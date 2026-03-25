from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import uuid

from core.db import get_db_connection

router = APIRouter()

class AdvanceRequest(BaseModel):
    days_offset: int

@router.post("/api/simulate/advance")
def advance_simulation(request: AdvanceRequest):
    if request.days_offset < 0 or request.days_offset > 30:
        raise HTTPException(status_code=400, detail="Offset must be between 0 and 30")
        
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    cur = conn.cursor()
    try:
        # 1. Update global simulated date in companies
        today = datetime.now().date()
        simulated_now = today + timedelta(days=request.days_offset)
        
        # We assume one company for this hackathon context
        cur.execute("SELECT id, plaid_current_balance, current_simulated_date FROM companies LIMIT 1;")
        company = cur.fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
            
        company_id = company['id']
        current_balance = float(company['plaid_current_balance'])
        
        # Update the simulation date
        cur.execute("UPDATE companies SET current_simulated_date = %s WHERE id = %s;", (simulated_now, company_id))
        
        # 2. Closed-Loop Reconciliation: Clear passed pending obligations
        cur.execute("SELECT id, entity_id, amount, due_date FROM obligations WHERE status = 'PENDING' AND due_date <= %s;", (simulated_now,))
        due_obs = cur.fetchall()
        
        for ob in due_obs:
            amount = float(ob['amount'])
            
            # Mark PAID
            cur.execute("UPDATE obligations SET status = 'PAID' WHERE id = %s;", (ob['id'],))
            
            # Create Transaction
            cur.execute(
                "INSERT INTO transactions (entity_id, amount, cleared_date, source) VALUES (%s, %s, %s, %s);",
                (ob['entity_id'], amount, simulated_now, 'SIMULATION_ADVANCEMENT')
            )
            
            # Update Balance (amount is negative for payables, positive for receivables)
            current_balance += amount
            
        # Write back the new balance
        cur.execute("UPDATE companies SET plaid_current_balance = %s WHERE id = %s;", (current_balance, company_id))
            
        # 3. Chaos Generation (discover 3-5 new random obligations if offset > 10)
        # We ensure this only happens once per session by checking a flag or just by the fact it naturally triggers
        # Actually, let's inject 3 to 5 items ONLY if they haven't been injected for this offset threshold yet.
        # Simple heuristic: look for obligations named 'UNEXPECTED_%'
        if request.days_offset > 10:
            cur.execute("SELECT count(*) as c FROM obligations WHERE status = 'PENDING' AND is_locked = FALSE AND amount < -100;")
            row = cur.fetchone()
            if row and row['c'] < 3:
                for _ in range(random.randint(3, 5)):
                    cur.execute("SELECT id FROM entities WHERE entity_type = 'VENDOR' ORDER BY random() LIMIT 1;")
                    vendor = cur.fetchone()
                    if vendor:
                        chaos_amount = round(random.uniform(-150.0, -900.0), 2)
                        chaos_due = simulated_now + timedelta(days=random.randint(2, 8))
                        cur.execute(
                            "INSERT INTO obligations (entity_id, amount, due_date, status, is_locked) "
                            "VALUES (%s, %s, %s, %s, %s);",
                            (vendor['id'], chaos_amount, chaos_due, 'PENDING', False)
                        )
        
        # 4. Predictive Breach Detection
        # Calculate phantom balance @ simulated_now + 7 days
        # Phantom = current_balance + sum(pending over next 7 days)
        horizon = simulated_now + timedelta(days=7)
        cur.execute("SELECT SUM(amount) as net_pending FROM obligations WHERE status = 'PENDING' AND due_date <= %s;", (horizon,))
        row = cur.fetchone()
        net_pending = float(row['net_pending']) if row and row['net_pending'] else 0.0
        
        phantom_balance = current_balance + net_pending
        
        if phantom_balance < 0:
            cur.execute("SELECT id FROM action_logs WHERE execution_type = 'SYSTEM_ALERT' LIMIT 1;")
            recent_log = cur.fetchone()
            
            if not recent_log:
                import json
                cot = json.dumps({"reason": "Phantom Balance dropped below zero", "projected_balance": phantom_balance, "horizon": horizon.isoformat()})
                payload = json.dumps({"action": "Liquidity Breach warning."})
                cur.execute(
                    "INSERT INTO action_logs (company_id, action_type, message, status, chain_of_thought, execution_type, execution_payload, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
                    (company_id, 'URGENT', 'Liquidity Breach Detected', 'PENDING_USER', cot, 'SYSTEM_ALERT', payload, simulated_now)
                )

        # 5. Evolve Inbox Logic
        # Day 5: "Proposed Negotiation with Vendor A"
        # Day 15: "URGENT: Liquidity Breach Imminent. Emergency Flash Sale Recommended."
        cur.execute("SELECT id, created_at FROM action_logs WHERE execution_type = 'SYSTEM_ALERT' AND status != 'RESOLVED';")
        logs = cur.fetchall()
        for log in logs:
            age = (simulated_now - log['created_at'].date()).days if hasattr(log['created_at'], 'date') else (simulated_now - log['created_at']).days
            if age >= 15:
                cur.execute("UPDATE action_logs SET message = 'URGENT: Liquidity Breach Imminent. Emergency Flash Sale Recommended.' WHERE id = %s;", (log['id'],))
            elif age >= 5:
                cur.execute("UPDATE action_logs SET message = 'Proposed Negotiation with Vendor A to extend terms.' WHERE id = %s;", (log['id'],))

        conn.commit()
        return {
            "message": "Simulation advanced successfully",
            "simulated_as_of": simulated_now.isoformat(),
            "new_balance": current_balance,
            "cleared_obligations": len(due_obs)
        }
    except Exception as e:
        conn.rollback()
        print(f"Error in simulation advance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
