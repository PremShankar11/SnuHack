"""
Test script for Quant Engine (Stream 2)
Tests all deterministic calculation modules
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from quant.runway import calculate_runway
from quant.phantom_balance import calculate_usable_cash
from quant.monte_carlo import monte_carlo_simulation
from quant.optimizer import optimize_payments


def test_runway_engine():
    """Test runway calculation"""
    print("\n=== Testing Runway Engine ===")
    
    balance = 10000.0
    today = datetime.now().date()
    
    obligations = [
        {'amount': -2000.0, 'due_date': today + timedelta(days=5)},
        {'amount': -3000.0, 'due_date': today + timedelta(days=10)},
        {'amount': -6000.0, 'due_date': today + timedelta(days=15)},  # This causes breach
    ]
    
    result = calculate_runway(balance, obligations)
    print(f"Balance: ${balance}")
    print(f"Days to Zero: {result['days_to_zero']}")
    print(f"Breach Date: {result['breach_date']}")
    
    assert result['days_to_zero'] == 15
    assert result['breach_date'] is not None
    print("✓ Runway engine test passed")


def test_phantom_balance():
    """Test phantom balance calculation"""
    print("\n=== Testing Phantom Balance ===")
    
    balance = 10000.0
    
    entities = {
        'entity1': {'ontology_tier': 0, 'name': 'IRS'},  # Tier 0 - locked
        'entity2': {'ontology_tier': 2, 'name': 'Vendor A'},  # Tier 2 - flexible
    }
    
    obligations = [
        {'entity_id': 'entity1', 'amount': -3000.0},  # Locked
        {'entity_id': 'entity2', 'amount': -2000.0},  # Not locked
    ]
    
    result = calculate_usable_cash(balance, obligations, entities)
    print(f"Balance: ${balance}")
    print(f"Locked Amount: ${result['locked_amount']}")
    print(f"Usable Cash: ${result['usable_cash']}")
    
    assert result['locked_amount'] == 3000.0
    assert result['usable_cash'] == 7000.0
    print("✓ Phantom balance test passed")


def test_monte_carlo():
    """Test Monte Carlo simulation"""
    print("\n=== Testing Monte Carlo Simulation ===")
    
    balance = 10000.0
    today = datetime.now().date()
    
    entities = {
        'entity1': {'avg_latency_days': 5},
        'entity2': {'avg_latency_days': 3},
    }
    
    obligations = [
        {'entity_id': 'entity1', 'amount': -4000.0, 'due_date': today + timedelta(days=10)},
        {'entity_id': 'entity2', 'amount': -4000.0, 'due_date': today + timedelta(days=15)},
    ]
    
    result = monte_carlo_simulation(balance, obligations, entities, simulations=100)
    print(f"Balance: ${balance}")
    print(f"Survival Probability: {result['survival_probability']}")
    
    assert 0.0 <= result['survival_probability'] <= 1.0
    print("✓ Monte Carlo test passed")


def test_optimizer():
    """Test linear programming optimizer"""
    print("\n=== Testing LP Optimizer ===")
    
    balance = 5000.0
    
    entities = {
        'entity1': {
            'name': 'IRS',
            'ontology_tier': 0,  # Must pay
            'late_fee_rate': 0.05,
            'goodwill_score': 100
        },
        'entity2': {
            'name': 'Vendor A',
            'ontology_tier': 2,
            'late_fee_rate': 0.02,
            'goodwill_score': 85
        },
        'entity3': {
            'name': 'Vendor B',
            'ontology_tier': 3,
            'late_fee_rate': 0.01,
            'goodwill_score': 70
        }
    }
    
    obligations = [
        {'id': 'ob1', 'entity_id': 'entity1', 'amount': -2000.0},  # Tier 0 - must pay
        {'id': 'ob2', 'entity_id': 'entity2', 'amount': -2500.0},  # Can optimize
        {'id': 'ob3', 'entity_id': 'entity3', 'amount': -1500.0},  # Can optimize
    ]
    
    result = optimize_payments(balance, obligations, entities)
    print(f"Balance: ${balance}")
    print(f"Total Obligations: ${sum(abs(ob['amount']) for ob in obligations)}")
    print("\nOptimization Results:")
    
    for decision in result['optimization_result']:
        print(f"  {decision['entity_name']}: {decision['math_decision']}")
        print(f"    Pay Now: ${decision['pay_now_amount']}")
        print(f"    Delay: ${decision['delay_amount']}")
    
    # Verify Tier 0 is fully paid
    tier0_decision = next(d for d in result['optimization_result'] if d['entity_name'] == 'IRS')
    assert tier0_decision['math_decision'] == 'FULL'
    print("\n✓ Optimizer test passed")


def test_integration():
    """Test full integration with database"""
    print("\n=== Testing Database Integration ===")
    
    try:
        from core.db import get_db_connection
        
        conn = get_db_connection()
        if not conn:
            print("⚠ Database connection failed - skipping integration test")
            return
        
        cur = conn.cursor()
        
        # Test query
        cur.execute("SELECT COUNT(*) as count FROM obligations WHERE status = 'PENDING';")
        result = cur.fetchone()
        print(f"Found {result['count']} pending obligations in database")
        
        cur.close()
        conn.close()
        
        print("✓ Database integration test passed")
    except Exception as e:
        print(f"⚠ Database integration test failed: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("QUANT ENGINE (STREAM 2) TEST SUITE")
    print("=" * 60)
    
    test_runway_engine()
    test_phantom_balance()
    test_monte_carlo()
    test_optimizer()
    test_integration()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
