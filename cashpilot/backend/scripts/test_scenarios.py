"""
Test Scenarios for Quant Engine
Inserts different data scenarios to verify engine responses
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import get_db_connection
from datetime import datetime, timedelta
import requests


def clear_test_data():
    """Clear existing test obligations"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Delete all pending obligations
        cur.execute("DELETE FROM obligations WHERE status = 'PENDING';")
        conn.commit()
        print("✓ Cleared existing test data")
    finally:
        cur.close()
        conn.close()


def get_company_and_entities():
    """Get company ID and entity IDs"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM companies LIMIT 1;")
        company = cur.fetchone()
        company_id = company['id'] if company else None
        
        cur.execute("SELECT id, name, ontology_tier FROM entities LIMIT 5;")
        entities = cur.fetchall()
        
        return company_id, entities
    finally:
        cur.close()
        conn.close()


def set_company_balance(balance: float):
    """Update company balance"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("UPDATE companies SET plaid_current_balance = %s WHERE id = (SELECT id FROM companies LIMIT 1);", (balance,))
        conn.commit()
        print(f"✓ Set company balance to ${balance:,.2f}")
    finally:
        cur.close()
        conn.close()


def insert_obligations(obligations: list):
    """Insert test obligations"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        for ob in obligations:
            cur.execute(
                "INSERT INTO obligations (entity_id, amount, due_date, status, is_locked) "
                "VALUES (%s, %s, %s, %s, %s);",
                (ob['entity_id'], ob['amount'], ob['due_date'], 'PENDING', ob.get('is_locked', False))
            )
        conn.commit()
        print(f"✓ Inserted {len(obligations)} obligations")
    finally:
        cur.close()
        conn.close()


def fetch_dashboard():
    """Fetch dashboard data from Quant Engine"""
    try:
        response = requests.get("http://localhost:8000/quant/api/dashboard")
        if response.ok:
            return response.json()
        else:
            print(f"✗ Dashboard fetch failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error fetching dashboard: {e}")
        return None


def fetch_decision():
    """Fetch decision data from Quant Engine"""
    try:
        response = requests.get("http://localhost:8000/quant/api/decision")
        if response.ok:
            return response.json()
        else:
            print(f"✗ Decision fetch failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error fetching decision: {e}")
        return None


def print_results(scenario_name: str, dashboard: dict, decision: dict):
    """Print scenario results"""
    print("\n" + "="*70)
    print(f"SCENARIO: {scenario_name}")
    print("="*70)
    
    if dashboard:
        state = dashboard['global_state']
        metrics = state['runway_metrics']
        
        print(f"\n📊 Dashboard Metrics:")
        print(f"  Balance:              ${state['plaid_balance']:,.2f}")
        print(f"  Phantom Usable:       ${state['phantom_usable_cash']:,.2f}")
        print(f"  Locked Tier 0:        ${state['locked_tier_0_funds']:,.2f}")
        print(f"  Days to Zero:         {metrics['days_to_zero']}")
        print(f"  Breach Date:          {metrics['liquidity_breach_date'] or 'None'}")
        print(f"  Survival Probability: {metrics['monte_carlo_survival_prob']*100:.1f}%")
    
    if decision:
        directive = decision['solver_directive']
        
        print(f"\n💡 LP Optimizer Results:")
        print(f"  Breach Amount:        ${directive['breach_amount']:,.2f}")
        print(f"  Obligations:          {len(directive['optimization_result'])}")
        
        for result in directive['optimization_result']:
            decision_emoji = "✅" if result['math_decision'] == "FULL" else "⚠️" if result['math_decision'] == "FRACTIONAL_PAYMENT" else "🔴"
            print(f"\n  {decision_emoji} {result['entity_name']}")
            print(f"     Decision:   {result['math_decision']}")
            print(f"     Pay Now:    ${result['pay_now_amount']:,.2f}")
            print(f"     Delay:      ${result['delay_amount']:,.2f}")
            print(f"     Extension:  {result['requested_extension_days']} days")


# ============================================================================
# SCENARIO 1: Healthy Cash Position (No Stress)
# ============================================================================
def scenario_1_healthy():
    """Scenario 1: Plenty of cash, no liquidity issues"""
    print("\n" + "🟢 " * 35)
    print("SCENARIO 1: HEALTHY CASH POSITION")
    print("🟢 " * 35)
    
    clear_test_data()
    company_id, entities = get_company_and_entities()
    
    # Set high balance
    set_company_balance(50000.00)
    
    # Add small obligations
    today = datetime.now().date()
    obligations = [
        {'entity_id': entities[0]['id'], 'amount': -500.00, 'due_date': today + timedelta(days=5)},
        {'entity_id': entities[1]['id'], 'amount': -750.00, 'due_date': today + timedelta(days=10)},
        {'entity_id': entities[2]['id'], 'amount': -300.00, 'due_date': today + timedelta(days=15)},
    ]
    
    insert_obligations(obligations)
    
    dashboard = fetch_dashboard()
    decision = fetch_decision()
    
    print_results("Healthy Cash Position", dashboard, decision)


# ============================================================================
# SCENARIO 2: Liquidity Breach (Critical Stress)
# ============================================================================
def scenario_2_breach():
    """Scenario 2: Insufficient cash, liquidity breach imminent"""
    print("\n" + "🔴 " * 35)
    print("SCENARIO 2: LIQUIDITY BREACH")
    print("🔴 " * 35)
    
    clear_test_data()
    company_id, entities = get_company_and_entities()
    
    # Set low balance
    set_company_balance(5000.00)
    
    # Add large obligations
    today = datetime.now().date()
    obligations = [
        {'entity_id': entities[0]['id'], 'amount': -3000.00, 'due_date': today + timedelta(days=3)},
        {'entity_id': entities[1]['id'], 'amount': -2500.00, 'due_date': today + timedelta(days=5)},
        {'entity_id': entities[2]['id'], 'amount': -1500.00, 'due_date': today + timedelta(days=7)},
    ]
    
    insert_obligations(obligations)
    
    dashboard = fetch_dashboard()
    decision = fetch_decision()
    
    print_results("Liquidity Breach", dashboard, decision)


# ============================================================================
# SCENARIO 3: Tier 0 Lock (Critical Obligations)
# ============================================================================
def scenario_3_tier0():
    """Scenario 3: Tier 0 obligations lock funds"""
    print("\n" + "🟡 " * 35)
    print("SCENARIO 3: TIER 0 OBLIGATIONS")
    print("🟡 " * 35)
    
    clear_test_data()
    company_id, entities = get_company_and_entities()
    
    # Find or create Tier 0 entity
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Update first entity to Tier 0
        cur.execute("UPDATE entities SET ontology_tier = 0 WHERE id = %s;", (entities[0]['id'],))
        conn.commit()
        print(f"✓ Set {entities[0]['name']} to Tier 0")
    finally:
        cur.close()
        conn.close()
    
    # Set moderate balance
    set_company_balance(10000.00)
    
    # Add obligations including Tier 0
    today = datetime.now().date()
    obligations = [
        {'entity_id': entities[0]['id'], 'amount': -6000.00, 'due_date': today + timedelta(days=5), 'is_locked': True},  # Tier 0
        {'entity_id': entities[1]['id'], 'amount': -3000.00, 'due_date': today + timedelta(days=7)},
        {'entity_id': entities[2]['id'], 'amount': -2000.00, 'due_date': today + timedelta(days=10)},
    ]
    
    insert_obligations(obligations)
    
    dashboard = fetch_dashboard()
    decision = fetch_decision()
    
    print_results("Tier 0 Obligations", dashboard, decision)
    
    # Reset entity back to original tier
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE entities SET ontology_tier = 2 WHERE id = %s;", (entities[0]['id'],))
        conn.commit()
    finally:
        cur.close()
        conn.close()


# ============================================================================
# SCENARIO 4: Fractional Payment Optimization
# ============================================================================
def scenario_4_fractional():
    """Scenario 4: Optimizer suggests fractional payments"""
    print("\n" + "🟠 " * 35)
    print("SCENARIO 4: FRACTIONAL PAYMENT OPTIMIZATION")
    print("🟠 " * 35)
    
    clear_test_data()
    company_id, entities = get_company_and_entities()
    
    # Set balance just below total obligations
    set_company_balance(8000.00)
    
    # Add obligations totaling more than balance
    today = datetime.now().date()
    obligations = [
        {'entity_id': entities[0]['id'], 'amount': -3500.00, 'due_date': today + timedelta(days=3)},
        {'entity_id': entities[1]['id'], 'amount': -3000.00, 'due_date': today + timedelta(days=5)},
        {'entity_id': entities[2]['id'], 'amount': -2500.00, 'due_date': today + timedelta(days=7)},
    ]
    
    insert_obligations(obligations)
    
    dashboard = fetch_dashboard()
    decision = fetch_decision()
    
    print_results("Fractional Payment Optimization", dashboard, decision)


# ============================================================================
# SCENARIO 5: High Latency Risk (Monte Carlo Stress)
# ============================================================================
def scenario_5_latency():
    """Scenario 5: High payment latency increases risk"""
    print("\n" + "🟣 " * 35)
    print("SCENARIO 5: HIGH LATENCY RISK")
    print("🟣 " * 35)
    
    clear_test_data()
    company_id, entities = get_company_and_entities()
    
    # Update entities with high latency
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        for entity in entities[:3]:
            cur.execute("UPDATE entities SET avg_latency_days = 10 WHERE id = %s;", (entity['id'],))
        conn.commit()
        print("✓ Set high latency (10 days) for entities")
    finally:
        cur.close()
        conn.close()
    
    # Set moderate balance
    set_company_balance(12000.00)
    
    # Add obligations with tight timing
    today = datetime.now().date()
    obligations = [
        {'entity_id': entities[0]['id'], 'amount': -4000.00, 'due_date': today + timedelta(days=8)},
        {'entity_id': entities[1]['id'], 'amount': -4000.00, 'due_date': today + timedelta(days=12)},
        {'entity_id': entities[2]['id'], 'amount': -4000.00, 'due_date': today + timedelta(days=16)},
    ]
    
    insert_obligations(obligations)
    
    dashboard = fetch_dashboard()
    decision = fetch_decision()
    
    print_results("High Latency Risk", dashboard, decision)
    
    # Reset latency
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE entities SET avg_latency_days = 0;")
        conn.commit()
    finally:
        cur.close()
        conn.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("QUANT ENGINE TEST SCENARIOS")
    print("="*70)
    print("\nThis script will test 5 different financial scenarios:")
    print("  1. Healthy Cash Position (No Stress)")
    print("  2. Liquidity Breach (Critical Stress)")
    print("  3. Tier 0 Obligations (Locked Funds)")
    print("  4. Fractional Payment Optimization")
    print("  5. High Latency Risk (Monte Carlo Stress)")
    print("\nMake sure the backend is running: python main.py")
    print("="*70)
    
    input("\nPress Enter to start testing...")
    
    # Run all scenarios
    scenario_1_healthy()
    input("\nPress Enter for next scenario...")
    
    scenario_2_breach()
    input("\nPress Enter for next scenario...")
    
    scenario_3_tier0()
    input("\nPress Enter for next scenario...")
    
    scenario_4_fractional()
    input("\nPress Enter for next scenario...")
    
    scenario_5_latency()
    
    print("\n" + "="*70)
    print("ALL SCENARIOS COMPLETED")
    print("="*70)
    print("\nYou can now:")
    print("  1. View the dashboard: http://localhost:3000")
    print("  2. View analytics: http://localhost:3000/analytics")
    print("  3. Check API docs: http://localhost:8000/docs")
    print("\nThe frontend will show the results from the last scenario.")
    print("="*70)
