from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import json

from core.db import get_db_connection

router = APIRouter()

class AdvanceRequest(BaseModel):
    days_offset: int

@router.post("/api/simulate/advance")
def advance_simulation(request: AdvanceRequest):
    """
    Simulation advance with dynamic obligation lifecycle.
    
    When slider moves:
    1. Updates simulated date
    2. Resolves obligations that fall within the simulation window (marks as PAID, updates balance)
    3. Dynamically generates new obligations (bills arriving, surprise expenses)
    4. Updates goodwill scores based on payment timeliness
    5. Detects liquidity breaches and generates action log alerts
    """
    if request.days_offset < 0 or request.days_offset > 30:
        raise HTTPException(status_code=400, detail="Offset must be between 0 and 30")
        
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    cur = conn.cursor()
    try:
        today = datetime.now().date()
        simulated_now = today + timedelta(days=request.days_offset)
        
        cur.execute("SELECT id, plaid_current_balance, current_simulated_date FROM companies LIMIT 1;")
        company = cur.fetchone()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
            
        company_id = company['id']
        prev_simulated = company['current_simulated_date']
        base_balance = float(company['plaid_current_balance'])
        
        # 1. Update simulated date
        cur.execute("UPDATE companies SET current_simulated_date = %s WHERE id = %s;", (simulated_now, company_id))
        
        # 2. Resolve obligations due between today and simulated_now
        # These get marked as PAID and balance is adjusted
        cur.execute(
            "SELECT id, entity_id, amount, due_date, is_locked FROM obligations "
            "WHERE status = 'PENDING' AND due_date > %s AND due_date <= %s ORDER BY due_date;",
            (today, simulated_now)
        )
        due_obs = cur.fetchall()
        
        resolved_count = 0
        running_balance = base_balance
        goodwill_changes = []
        
        for ob in due_obs:
            amount = float(ob['amount'])
            days_early = (ob['due_date'] - today).days
            
            # Simulate realistic payment behavior
            if amount < 0:  # Payable
                # Locked (Tier 0) always pays
                if ob['is_locked']:
                    should_pay = True
                else:
                    # Non-locked: some get deferred, some paid on time
                    if days_early <= request.days_offset * 0.5:
                        should_pay = random.random() < 0.75  # 75% pay if well within window
                    else:
                        should_pay = random.random() < 0.55  # 55% for later ones
                
                if should_pay:
                    cur.execute("UPDATE obligations SET status = 'PAID' WHERE id = %s;", (ob['id'],))
                    cur.execute(
                        "INSERT INTO transactions (entity_id, amount, cleared_date, source) "
                        "VALUES (%s, %s, %s, 'SIMULATION_ADVANCE');",
                        (ob['entity_id'], amount, ob['due_date'])
                    )
                    running_balance += amount
                    resolved_count += 1
                    
                    # Goodwill: paying on time boosts, paying late hurts
                    overdue_days = max(0, (simulated_now - ob['due_date']).days)
                    if overdue_days <= 2:
                        gw_delta = random.randint(1, 3)
                        goodwill_changes.append((ob['entity_id'], gw_delta))
                    elif overdue_days > 5:
                        gw_delta = -random.randint(3, 8)
                        goodwill_changes.append((ob['entity_id'], gw_delta))
            
            else:  # Receivable
                # Client payments: some come through, some don't
                pay_prob = 0.6 if days_early <= request.days_offset * 0.6 else 0.35
                if random.random() < pay_prob:
                    cur.execute("UPDATE obligations SET status = 'PAID' WHERE id = %s;", (ob['id'],))
                    cur.execute(
                        "INSERT INTO transactions (entity_id, amount, cleared_date, source) "
                        "VALUES (%s, %s, %s, 'SIMULATION_ADVANCE');",
                        (ob['entity_id'], amount, ob['due_date'])
                    )
                    running_balance += amount
                    resolved_count += 1
                    # Successful client payment boosts goodwill
                    goodwill_changes.append((ob['entity_id'], random.randint(2, 5)))
        
        # Update balance
        cur.execute("UPDATE companies SET plaid_current_balance = %s WHERE id = %s;", (running_balance, company_id))
        
        # 3. Apply goodwill changes
        for entity_id, delta in goodwill_changes:
            if delta > 0:
                cur.execute(
                    "UPDATE entities SET goodwill_score = LEAST(100, goodwill_score + %s) WHERE id = %s;",
                    (delta, entity_id)
                )
            else:
                cur.execute(
                    "UPDATE entities SET goodwill_score = GREATEST(0, goodwill_score + %s) WHERE id = %s;",
                    (delta, entity_id)
                )
        
        # 4. Dynamic obligation generation (new bills appear as time passes)
        new_obligations = 0
        cur.execute("SELECT id, ontology_tier FROM entities WHERE entity_type = 'VENDOR';")
        vendor_list = cur.fetchall()
        cur.execute("SELECT id FROM entities WHERE entity_type = 'CLIENT';")
        client_list = cur.fetchall()
        
        if request.days_offset > 5:
            # Generate 2-4 new surprise obligations
            for _ in range(random.randint(2, 4)):
                if vendor_list and random.random() < 0.7:
                    vendor = random.choice(vendor_list)
                    chaos_amount = round(random.uniform(-150.0, -1500.0), 2)
                    chaos_due = simulated_now + timedelta(days=random.randint(2, 10))
                    # Check if similar already exists to avoid duplicates
                    cur.execute(
                        "SELECT count(*) as c FROM obligations WHERE entity_id = %s AND due_date = %s AND status = 'PENDING';",
                        (vendor['id'], chaos_due)
                    )
                    if cur.fetchone()['c'] == 0:
                        cur.execute(
                            "INSERT INTO obligations (entity_id, amount, due_date, status, is_locked) "
                            "VALUES (%s, %s, %s, 'PENDING', %s);",
                            (vendor['id'], chaos_amount, chaos_due, vendor['ontology_tier'] <= 1)
                        )
                        new_obligations += 1
            
            # Some new receivables too (clients sending new orders)
            if client_list and random.random() < 0.5:
                client = random.choice(client_list)
                recv_amount = round(random.uniform(500.0, 3000.0), 2)
                recv_due = simulated_now + timedelta(days=random.randint(3, 12))
                cur.execute(
                    "INSERT INTO obligations (entity_id, amount, due_date, status, is_locked) "
                    "VALUES (%s, %s, %s, 'PENDING', FALSE);",
                    (client['id'], recv_amount, recv_due)
                )
                new_obligations += 1
        
        # 5. Liquidity Breach Detection
        horizon = simulated_now + timedelta(days=7)
        cur.execute(
            "SELECT COALESCE(SUM(amount), 0) as net FROM obligations WHERE status = 'PENDING' AND due_date > %s AND due_date <= %s;",
            (simulated_now, horizon)
        )
        upcoming_net = float(cur.fetchone()['net'])
        phantom_balance = running_balance + upcoming_net
        breach_detected = phantom_balance < 0 or running_balance < 500
        
        # Generate action log alerts for breaches
        if breach_detected:
            cur.execute("SELECT id FROM action_logs WHERE action_type = 'URGENT' AND is_resolved = FALSE LIMIT 1;")
            existing = cur.fetchone()
            if not existing:
                cot = json.dumps({
                    "reason": f"Projected phantom balance ${phantom_balance:,.2f} within 7 days",
                    "current_balance": running_balance,
                    "upcoming_obligations": upcoming_net,
                    "horizon": horizon.isoformat()
                })
                severity = 'URGENT' if phantom_balance < -1000 else 'HIGH'
                msg = f"LIQUIDITY BREACH: Balance projected to ${phantom_balance:,.2f} by {horizon.strftime('%b %d')}"
                if running_balance < 500:
                    msg = f"CRITICAL: Current balance ${running_balance:,.2f} — below safety threshold"
                
                cur.execute(
                    "INSERT INTO action_logs (company_id, action_type, message, status, chain_of_thought, "
                    "execution_type, execution_payload, created_at) "
                    "VALUES (%s, %s, %s, 'PENDING_USER', %s, 'SYSTEM_ALERT', %s, %s);",
                    (company_id, severity, msg, cot,
                     json.dumps({"action": "Defer non-locked payables or trigger emergency cash injection"}),
                     simulated_now)
                )
        
        # If balance recovered and old alerts exist, resolve them
        if running_balance > 2000 and not breach_detected:
            cur.execute(
                "UPDATE action_logs SET is_resolved = TRUE, status = 'RESOLVED' "
                "WHERE action_type IN ('URGENT', 'HIGH') AND is_resolved = FALSE;"
            )
        
        # 6. Evolve existing alerts by age
        cur.execute("SELECT id, created_at FROM action_logs WHERE is_resolved = FALSE;")
        for log in cur.fetchall():
            log_date = log['created_at'].date() if hasattr(log['created_at'], 'date') else log['created_at']
            age = (simulated_now - log_date).days
            if age >= 12:
                cur.execute(
                    "UPDATE action_logs SET action_type = 'URGENT', "
                    "message = 'CRITICAL: Unresolved liquidity issue for ' || %s || ' days. Immediate action required.' "
                    "WHERE id = %s;", (str(age), log['id'])
                )

        conn.commit()

        escalation = None
        try:
            from services.whatsapp_escalation import maybe_send_defcon1_whatsapp

            escalation = maybe_send_defcon1_whatsapp(str(company_id))
        except Exception as escalation_error:
            escalation = {
                "triggered": False,
                "reason": f"Escalation failed: {escalation_error}",
            }
        
        return {
            "message": "Simulation advanced",
            "simulated_as_of": simulated_now.isoformat(),
            "new_balance": running_balance,
            "resolved_obligations": resolved_count,
            "new_obligations": new_obligations,
            "breach_detected": breach_detected,
            "phantom_balance": phantom_balance,
            "goodwill_updates": len(goodwill_changes),
            "defcon1_escalation": escalation,
        }
    except Exception as e:
        conn.rollback()
        print(f"Error in simulation advance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
