"""
Demo script to test Quant Engine API endpoints
Requires the FastAPI server to be running
"""
import requests
import json


BASE_URL = "http://localhost:8000/quant"


def test_dashboard_endpoint():
    """Test GET /api/dashboard"""
    print("\n" + "="*60)
    print("Testing Dashboard Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard")
        response.raise_for_status()
        
        data = response.json()
        
        print("\n✓ Dashboard Response:")
        print(json.dumps(data, indent=2))
        
        # Extract key metrics
        state = data.get('global_state', {})
        print(f"\nKey Metrics:")
        print(f"  Plaid Balance: ${state.get('plaid_balance', 0):,.2f}")
        print(f"  Usable Cash: ${state.get('phantom_usable_cash', 0):,.2f}")
        print(f"  Locked Funds: ${state.get('locked_tier_0_funds', 0):,.2f}")
        
        runway = state.get('runway_metrics', {})
        print(f"\nRunway Metrics:")
        print(f"  Days to Zero: {runway.get('days_to_zero', 'N/A')}")
        print(f"  Breach Date: {runway.get('breach_date', 'None')}")
        print(f"  Survival Probability: {runway.get('monte_carlo_survival_prob', 0):.2%}")
        
        return True
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
        print("  Make sure the FastAPI server is running:")
        print("  cd backend && python main.py")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_decision_endpoint():
    """Test GET /api/decision"""
    print("\n" + "="*60)
    print("Testing Decision Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/decision")
        response.raise_for_status()
        
        data = response.json()
        
        print("\n✓ Decision Response:")
        print(json.dumps(data, indent=2))
        
        # Extract optimization results
        directive = data.get('solver_directive', {})
        print(f"\nBreach Amount: ${directive.get('breach_amount', 0):,.2f}")
        
        results = directive.get('optimization_result', [])
        if results:
            print(f"\nOptimization Decisions ({len(results)} obligations):")
            for i, decision in enumerate(results[:5], 1):  # Show first 5
                print(f"\n  {i}. {decision.get('entity_name', 'Unknown')}")
                print(f"     Decision: {decision.get('math_decision', 'N/A')}")
                print(f"     Pay Now: ${decision.get('pay_now_amount', 0):,.2f}")
                print(f"     Delay: ${decision.get('delay_amount', 0):,.2f}")
                print(f"     Extension: {decision.get('requested_extension_days', 0)} days")
            
            if len(results) > 5:
                print(f"\n  ... and {len(results) - 5} more")
        else:
            print("\n  No optimization decisions (no pending obligations)")
        
        return True
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_api_docs():
    """Check if API docs are accessible"""
    print("\n" + "="*60)
    print("API Documentation")
    print("="*60)
    
    print("\nInteractive API docs available at:")
    print(f"  Swagger UI: {BASE_URL}/docs")
    print(f"  ReDoc: {BASE_URL}/redoc")


if __name__ == "__main__":
    print("="*60)
    print("QUANT ENGINE API DEMO")
    print("="*60)
    
    # Test endpoints
    dashboard_ok = test_dashboard_endpoint()
    decision_ok = test_decision_endpoint()
    test_api_docs()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Dashboard Endpoint: {'✓ PASS' if dashboard_ok else '✗ FAIL'}")
    print(f"Decision Endpoint: {'✓ PASS' if decision_ok else '✗ FAIL'}")
    
    if dashboard_ok and decision_ok:
        print("\n✓ All API endpoints are working correctly!")
    else:
        print("\n✗ Some endpoints failed. Check server logs.")
    
    print("="*60)
