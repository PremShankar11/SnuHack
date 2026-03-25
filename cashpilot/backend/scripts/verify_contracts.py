"""
Verify that API responses match shared_contracts.json exactly
"""
import requests
import json


BASE_URL = "http://localhost:8000/quant"


def verify_dashboard_contract():
    """Verify dashboard endpoint matches global_state contract"""
    print("\n" + "="*60)
    print("Verifying Dashboard Contract")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/dashboard")
    data = response.json()
    
    required_fields = {
        'global_state': {
            'simulated_as_of': str,
            'plaid_balance': (int, float),
            'phantom_usable_cash': (int, float),
            'locked_tier_0_funds': (int, float),
            'runway_metrics': {
                'days_to_zero': int,
                'liquidity_breach_date': (str, type(None)),
                'monte_carlo_survival_prob': (int, float)
            },
            'cashflow_projection_array': list
        }
    }
    
    def check_structure(data, schema, path=""):
        """Recursively check data structure"""
        for key, expected_type in schema.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in data:
                print(f"❌ Missing field: {current_path}")
                return False
            
            value = data[key]
            
            if isinstance(expected_type, dict):
                if not isinstance(value, dict):
                    print(f"❌ {current_path} should be dict, got {type(value)}")
                    return False
                if not check_structure(value, expected_type, current_path):
                    return False
            elif isinstance(expected_type, tuple):
                if not isinstance(value, expected_type):
                    print(f"❌ {current_path} should be {expected_type}, got {type(value)}")
                    return False
            elif expected_type == list:
                if not isinstance(value, list):
                    print(f"❌ {current_path} should be list, got {type(value)}")
                    return False
            else:
                if not isinstance(value, expected_type):
                    print(f"❌ {current_path} should be {expected_type}, got {type(value)}")
                    return False
            
            print(f"✓ {current_path}: {type(value).__name__}")
        
        return True
    
    success = check_structure(data, required_fields)
    
    # Check cashflow_projection_array structure
    if 'global_state' in data and 'cashflow_projection_array' in data['global_state']:
        projections = data['global_state']['cashflow_projection_array']
        if projections:
            first = projections[0]
            if 'date' in first and 'balance' in first:
                print(f"✓ cashflow_projection_array[0].date: {type(first['date']).__name__}")
                print(f"✓ cashflow_projection_array[0].balance: {type(first['balance']).__name__}")
            else:
                print("❌ cashflow_projection_array items missing date or balance")
                success = False
    
    return success


def verify_decision_contract():
    """Verify decision endpoint matches solver_directive contract"""
    print("\n" + "="*60)
    print("Verifying Decision Contract")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/decision")
    data = response.json()
    
    required_fields = {
        'solver_directive': {
            'breach_amount': (int, float),
            'optimization_result': list
        }
    }
    
    def check_structure(data, schema, path=""):
        """Recursively check data structure"""
        for key, expected_type in schema.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in data:
                print(f"❌ Missing field: {current_path}")
                return False
            
            value = data[key]
            
            if isinstance(expected_type, dict):
                if not isinstance(value, dict):
                    print(f"❌ {current_path} should be dict, got {type(value)}")
                    return False
                if not check_structure(value, expected_type, current_path):
                    return False
            elif isinstance(expected_type, tuple):
                if not isinstance(value, expected_type):
                    print(f"❌ {current_path} should be {expected_type}, got {type(value)}")
                    return False
            elif expected_type == list:
                if not isinstance(value, list):
                    print(f"❌ {current_path} should be list, got {type(value)}")
                    return False
            else:
                if not isinstance(value, expected_type):
                    print(f"❌ {current_path} should be {expected_type}, got {type(value)}")
                    return False
            
            print(f"✓ {current_path}: {type(value).__name__}")
        
        return True
    
    success = check_structure(data, required_fields)
    
    # Check optimization_result structure
    if 'solver_directive' in data and 'optimization_result' in data['solver_directive']:
        results = data['solver_directive']['optimization_result']
        if results:
            first = results[0]
            required_result_fields = [
                'obligation_id',
                'entity_name',
                'original_due',
                'math_decision',
                'pay_now_amount',
                'delay_amount',
                'requested_extension_days'
            ]
            
            for field in required_result_fields:
                if field in first:
                    print(f"✓ optimization_result[0].{field}: {type(first[field]).__name__}")
                else:
                    print(f"❌ optimization_result[0] missing field: {field}")
                    success = False
            
            # Verify math_decision values
            valid_decisions = ['FULL', 'FRACTIONAL_PAYMENT', 'DELAY']
            for result in results:
                if result['math_decision'] not in valid_decisions:
                    print(f"❌ Invalid math_decision: {result['math_decision']}")
                    success = False
            
            if all(r['math_decision'] in valid_decisions for r in results):
                print(f"✓ All math_decision values are valid")
    
    return success


if __name__ == '__main__':
    print("="*60)
    print("CONTRACT COMPLIANCE VERIFICATION")
    print("="*60)
    
    try:
        dashboard_ok = verify_dashboard_contract()
        decision_ok = verify_decision_contract()
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Dashboard Contract: {'✓ PASS' if dashboard_ok else '✗ FAIL'}")
        print(f"Decision Contract: {'✓ PASS' if decision_ok else '✗ FAIL'}")
        
        if dashboard_ok and decision_ok:
            print("\n✅ ALL CONTRACTS VERIFIED - 100% COMPLIANT")
        else:
            print("\n❌ CONTRACT VERIFICATION FAILED")
        
        print("="*60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the server is running: python main.py")
