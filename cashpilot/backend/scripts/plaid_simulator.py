import os
import sys
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import get_db_connection

def generate_simulator_data():
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to the database. Cannot run simulator.")
        return
    cur = conn.cursor()
    
    try:
        print("Fetching entities for simulation...")
        cur.execute("SELECT id, name, entity_type, ontology_tier FROM entities;")
        all_entities = cur.fetchall()
        
        vendors = [e for e in all_entities if e['entity_type'] == 'VENDOR']
        clients = [e for e in all_entities if e['entity_type'] == 'CLIENT']
        
        if not vendors and not clients:
            print("No entities found. Please run seed_data.py first.")
            return

        print("Simulating chronological time passing (-60 days to Today)...")
        today = datetime.now().date()
        current_date = today - timedelta(days=60)
        
        while current_date <= today:
            # 1. Randomly generate new bills/invoices on this day
            if vendors and random.random() < 0.2:  # 20% chance of a new Vendor Bill
                vendor = random.choice(vendors)
                amount = round(random.uniform(-50.0, -1000.0), 2)
                due_date = current_date + timedelta(days=random.randint(10, 30))
                is_locked = vendor['ontology_tier'] == 0
                cur.execute(
                    "INSERT INTO obligations (entity_id, amount, due_date, status, is_locked) "
                    "VALUES (%s, %s, %s, %s, %s);",
                    (vendor['id'], amount, due_date, 'PENDING', is_locked)
                )

            if clients and random.random() < 0.15:  # 15% chance of a new Client Invoice
                client = random.choice(clients)
                amount = round(random.uniform(300.0, 3000.0), 2)
                due_date = current_date + timedelta(days=random.randint(5, 20))
                cur.execute(
                    "INSERT INTO obligations (entity_id, amount, due_date, status, is_locked) "
                    "VALUES (%s, %s, %s, %s, %s);",
                    (client['id'], amount, due_date, 'PENDING', False)
                )
                
            # 2. Evaluate pending obligations for clearing/paying on this simulated day
            cur.execute("SELECT id, entity_id, amount, due_date FROM obligations WHERE status = 'PENDING';")
            pending_obs = cur.fetchall()
            
            for ob in pending_obs:
                days_until_due = (ob['due_date'] - current_date).days
                pay_today = False
                
                if float(ob['amount']) < 0: # Payable (Vendor)
                    # We usually pay bills 1 to 3 days early (prompt), sometimes late
                    if days_until_due in [1, 2, 3] and random.random() < 0.4:
                        pay_today = True # Paid beautifully on time/early
                    elif days_until_due < 0 and random.random() < 0.3:
                        pay_today = True # Realistically delayed
                else: # Receivable (Client)
                    # Clients usually pay around due date, sometimes stretch it
                    if days_until_due in [0, 1] and random.random() < 0.5:
                        pay_today = True
                    elif days_until_due < -2 and random.random() < 0.4:
                        pay_today = True
                
                if pay_today:
                    cur.execute("UPDATE obligations SET status = 'PAID' WHERE id = %s;", (ob['id'],))
                    cur.execute(
                        "INSERT INTO transactions (entity_id, amount, cleared_date, source) "
                        "VALUES (%s, %s, %s, %s);",
                        (ob['entity_id'], ob['amount'], current_date, 'PLAID_API_SIMULATOR')
                    )

            # Advance time context
            current_date += timedelta(days=1)


        conn.commit()
        print("Simulation data generation completed.")
        
    except Exception as e:
        conn.rollback()
        print("Error during simulation:", e)
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    generate_simulator_data()
