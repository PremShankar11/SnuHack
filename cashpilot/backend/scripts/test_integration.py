#!/usr/bin/env python3
"""
Integration Test Suite
Tests the complete flow from ingestion to optimization
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_dashboard_endpoint():
    """Test Quant Engine dashboard endpoint"""
    print("\n🧪 Testing GET /quant/api/dashboard...")
    
    response = requests.get(f"{BASE_URL}/quant/api/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        global_state = data.get('global_state', {})
        
        print(f"✅ Dashboard endpoint working")
        print(f"   Balance: ${global_state.get('plaid_balance', 0):,.2f}")
        print(f"   Phantom Usable: ${global_state.get('phantom_usable_cash', 0):,.2f}")
        print(f"   Days to Zero: {global_state.get('runway_metrics', {}).get('days_to_zero', 'N/A')}")
        print(f"   Survival Prob: {global_state.get('runway_metrics', {}).get('monte_carlo_survival_prob', 0):.2%}")
        
        return True
    else:
        print(f"❌ Dashboard endpoint failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_decision_endpoint():
    """Test LP Optimizer decision endpoint"""
    print("\n🧪 Testing GET /quant/api/decision...")
    
    response = requests.get(f"{BASE_URL}/quant/api/decision")
    
    if response.status_code == 200:
        data = response.json()
        solver = data.get('solver_directive', {})
        results = solver.get('optimization_result', [])
        
        print(f"✅ Decision endpoint working")
        print(f"   Breach Amount: ${solver.get('breach_amount', 0):,.2f}")
        print(f"   Optimization Results: {len(results)} obligations")
        
        for i, result in enumerate(results[:3]):  # Show first 3
            print(f"   [{i+1}] {result.get('entity_name')}: {result.get('math_decision')}")
            print(f"       Pay Now: ${result.get('pay_now_amount', 0):,.2f}, Delay: ${result.get('delay_amount', 0):,.2f}")
        
        return True
    else:
        print(f"❌ Decision endpoint failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_analytics_endpoint():
    """Test legacy analytics endpoint"""
    print("\n🧪 Testing GET /api/analytics...")
    
    response = requests.get(f"{BASE_URL}/api/analytics")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✅ Analytics endpoint working")
        print(f"   Cash Flow Points: {len(data.get('cashFlow', []))}")
        print(f"   Vendors: {len(data.get('vendors', []))}")
        print(f"   Monte Carlo Simulations: {data.get('monteCarlo', {}).get('simulations', 0)}")
        
        return True
    else:
        print(f"❌ Analytics endpoint failed: {response.status_code}")
        return False

def test_inbox_endpoint():
    """Test inbox endpoint"""
    print("\n🧪 Testing GET /api/inbox...")
    
    response = requests.get(f"{BASE_URL}/api/inbox")
    
    if response.status_code == 200:
        data = response.json()
        inbox = data.get('inbox', [])
        
        print(f"✅ Inbox endpoint working")
        print(f"   Action Items: {len(inbox)}")
        
        for i, item in enumerate(inbox[:3]):
            print(f"   [{i+1}] {item.get('priority').upper()}: {item.get('summary', '')[:60]}...")
        
        return True
    else:
        print(f"❌ Inbox endpoint failed: {response.status_code}")
        return False

def test_transactions_endpoint():
    """Test transactions endpoint"""
    print("\n🧪 Testing GET /api/transactions...")
    
    response = requests.get(f"{BASE_URL}/api/transactions")
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        
        print(f"✅ Transactions endpoint working")
        print(f"   Transactions: {len(items)}")
        
        for i, item in enumerate(items[:3]):
            print(f"   [{i+1}] {item.get('description', '')}: ${item.get('amount', 0):,.2f}")
        
        return True
    else:
        print(f"❌ Transactions endpoint failed: {response.status_code}")
        return False

def test_simulation_advance():
    """Test simulation advance endpoint"""
    print("\n🧪 Testing POST /api/simulate/advance...")
    
    payload = {"days_offset": 3}
    response = requests.post(
        f"{BASE_URL}/api/simulate/advance",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✅ Simulation advance working")
        print(f"   Simulated Date: {data.get('simulated_as_of')}")
        print(f"   New Balance: ${data.get('new_balance', 0):,.2f}")
        print(f"   Resolved Obligations: {data.get('resolved_obligations', 0)}")
        print(f"   New Obligations: {data.get('new_obligations', 0)}")
        print(f"   Breach Detected: {data.get('breach_detected', False)}")
        
        return True
    else:
        print(f"❌ Simulation advance failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_contract_compliance():
    """Verify API responses match shared_contracts.json schema"""
    print("\n🧪 Testing Contract Compliance...")
    
    # Test dashboard contract
    response = requests.get(f"{BASE_URL}/quant/api/dashboard")
    if response.status_code == 200:
        data = response.json()
        gs = data.get('global_state', {})
        
        required_fields = [
            'simulated_as_of', 'plaid_balance', 'phantom_usable_cash',
            'locked_tier_0_funds', 'runway_metrics', 'cashflow_projection_array'
        ]
        
        missing = [f for f in required_fields if f not in gs]
        
        if not missing:
            print(f"✅ Dashboard contract compliant")
        else:
            print(f"❌ Dashboard missing fields: {missing}")
            return False
    
    # Test decision contract
    response = requests.get(f"{BASE_URL}/quant/api/decision")
    if response.status_code == 200:
        data = response.json()
        sd = data.get('solver_directive', {})
        
        if 'breach_amount' in sd and 'optimization_result' in sd:
            print(f"✅ Decision contract compliant")
        else:
            print(f"❌ Decision contract missing fields")
            return False
    
    return True

def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("🚀 CashPilot Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Dashboard Endpoint", test_dashboard_endpoint),
        ("Decision Endpoint", test_decision_endpoint),
        ("Analytics Endpoint", test_analytics_endpoint),
        ("Inbox Endpoint", test_inbox_endpoint),
        ("Transactions Endpoint", test_transactions_endpoint),
        ("Simulation Advance", test_simulation_advance),
        ("Contract Compliance", test_contract_compliance),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check logs above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        sys.exit(1)
