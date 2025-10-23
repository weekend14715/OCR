#!/usr/bin/env python3
"""
Kim tra cu hnh webhook PayOS
"""
import requests
import json
import os
from datetime import datetime

SERVER_URL = "https://license-server-hjat.onrender.com"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def check_server_reachable():
    """Kim tra server c accessible khng"""
    print("1. Checking if server is reachable...")
    
    try:
        response = requests.get(SERVER_URL, timeout=10)
        print(f"    Server is reachable (Status: {response.status_code})")
        return True
    except requests.exceptions.Timeout:
        print(f"    Server timeout - May be sleeping (Free tier)")
        print(f"    Solution: Wait 30s and try again")
        return False
    except Exception as e:
        print(f"    Cannot reach server: {e}")
        return False

def check_webhook_endpoint():
    """Kim tra webhook endpoint"""
    print("\n2. Checking webhook endpoint...")
    
    endpoint = f"{SERVER_URL}/payos/webhook"
    
    try:
        # Try GET first (should return 405 Method Not Allowed)
        response = requests.get(endpoint, timeout=10)
        print(f"    GET {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 405:
            print(f"    Webhook endpoint exists (POST-only)")
        elif response.status_code == 404:
            print(f"    Webhook endpoint not found")
            print(f"    Check if payos_handler.py is loaded correctly")
            return False
        else:
            print(f"    Unexpected status: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"    Error: {e}")
        return False

def check_health_endpoint():
    """Kim tra health check endpoint"""
    print("\n3. Checking health endpoint...")
    
    endpoint = f"{SERVER_URL}/payos/health"
    
    try:
        response = requests.get(endpoint, timeout=10)
        print(f"   GET {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"    Health check passed")
            print(f"   Response: {json.dumps(data, indent=6)}")
            return True
        else:
            print(f"    Health check failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"    Error: {e}")
        return False

def test_webhook_manual():
    """Test webhook vi fake data"""
    print("\n4. Testing webhook with fake data...")
    
    endpoint = f"{SERVER_URL}/payos/webhook"
    
    fake_webhook_data = {
        "code": "00",
        "desc": "success",
        "data": {
            "orderCode": 123456,
            "amount": 200000,
            "description": "TEST_MACHINE_ID-1-test@example.com",
            "accountNumber": "12345678",
            "reference": "FT123456",
            "transactionDateTime": datetime.now().isoformat(),
            "currency": "VND",
            "paymentLinkId": "test-link-id",
            "code": "00",
            "desc": "Thnh cng",
            "counterAccountBankId": "",
            "counterAccountBankName": "",
            "counterAccountName": "",
            "counterAccountNumber": ""
        },
        "signature": "fake-signature-for-testing"
    }
    
    print(f"   POST {endpoint}")
    print(f"   Payload: {json.dumps(fake_webhook_data, indent=6, ensure_ascii=False)[:300]}...")
    
    try:
        response = requests.post(
            endpoint,
            json=fake_webhook_data,
            timeout=10
        )
        
        print(f"\n   Status: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print(f"\n    Webhook endpoint is working!")
            print(f"    Note: Signature verification may fail (expected)")
            return True
        elif response.status_code == 400:
            data = response.json()
            if "signature" in str(data).lower():
                print(f"\n    Webhook is working (signature verification active)")
                return True
            else:
                print(f"\n    Webhook returned 400 (may need debugging)")
                return False
        else:
            print(f"\n    Unexpected response")
            return False
            
    except Exception as e:
        print(f"    Error: {e}")
        return False

def check_env_vars():
    """Kim tra environment variables (local)"""
    print("\n5. Checking local environment variables...")
    
    required_vars = [
        "PAYOS_CLIENT_ID",
        "PAYOS_API_KEY", 
        "PAYOS_CHECKSUM_KEY",
        "PAYOS_WEBHOOK_SECRET"
    ]
    
    missing = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"    {var}: {'*' * 8}{os.getenv(var)[-4:]}")
        else:
            print(f"    {var}: Not set")
            missing.append(var)
    
    if missing:
        print(f"\n    Missing variables: {', '.join(missing)}")
        print(f"    These must be set on Render Dashboard")
        print(f"       Environment  Environment Variables")
        return False
    
    return True

def get_webhook_instructions():
    """Hng dn cu hnh webhook"""
    print_section("INSTRUCTIONS: Configure Webhook on PayOS")
    
    print("Step 1: Login to PayOS Dashboard")
    print("   URL: https://my.payos.vn/")
    print("   Login with your credentials")
    
    print("\nStep 2: Navigate to Webhook Settings")
    print("   Dashboard  Settings  Webhook Configuration")
    print("   or")
    print("   Dashboard  Ci t  Cu hnh Webhook")
    
    print("\nStep 3: Add Webhook URL")
    print(f"   URL: {SERVER_URL}/payos/webhook")
    print("   Method: POST")
    print("   Events:")
    print("     [x] payment.success")
    print("     [x] payment.failed") 
    print("     [x] payment.cancelled")
    
    print("\nStep 4: Save & Test")
    print("   PayOS will send a test request")
    print("   Your server should respond with 200 OK")
    print("   If successful -> Webhook is activated [OK]")
    
    print("\nStep 5: Verify")
    print("   Create a real payment and complete it")
    print("   Check Render logs for webhook receipt:")
    print("     [WEBHOOK] Received PayOS webhook")

def show_debugging_tips():
    """Tips  debug webhook"""
    print_section("DEBUGGING TIPS")
    
    print("1. Check Render Logs")
    print("   https://dashboard.render.com")
    print("    license-server-hjat  Logs")
    print("   Look for: [WEBHOOK] or [ERROR]")
    
    print("\n2. Check PayOS Webhook Logs")
    print("   https://my.payos.vn/")
    print("   -> Webhook Logs / Lich su Webhook")
    print("   Status codes:")
    print("     - 200 = Success")
    print("     - 400 = Bad request (check signature)")
    print("     - 500 = Server error (check logs)")
    print("     - Timeout = Server sleeping or slow")
    
    print("\n3. Manual Webhook Test")
    print("   Test webhook locally:")
    print(f"   curl -X POST {SERVER_URL}/payos/webhook \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"code\": \"00\", \"data\": {{\"orderCode\": 123}}}}'")
    
    print("\n4. Wake Up Render Service")
    print("   If server is sleeping:")
    print(f"   curl {SERVER_URL}/payos/health")
    print("   Wait 10 seconds, then configure webhook")
    
    print("\n5. Check Environment Variables on Render")
    print("   Dashboard  license-server-hjat")
    print("    Environment  Environment Variables")
    print("   Verify all PayOS keys are set correctly")

def main():
    print(f"\n{'#'*70}")
    print(f"#  WEBHOOK CONFIGURATION CHECKER")
    print(f"{'#'*70}")
    print(f"\nServer: {SERVER_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print_section("RUNNING CHECKS")
    
    results = {
        "server_reachable": check_server_reachable(),
        "webhook_endpoint": check_webhook_endpoint(),
        "health_endpoint": check_health_endpoint(),
        "webhook_manual_test": test_webhook_manual(),
        "env_vars": check_env_vars()
    }
    
    # Summary
    print_section("SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"   {status}  {check.replace('_', ' ').title()}")
    
    print(f"\n   Score: {passed}/{total} checks passed")
    
    if passed == total:
        print(f"\n   All checks passed!")
        print(f"   Your server is ready for PayOS webhook")
        get_webhook_instructions()
    else:
        print(f"\n   Some checks failed")
        print(f"   Please fix the issues above before configuring webhook")
        show_debugging_tips()
    
    print_section("NEXT STEPS")
    
    print("1. Configure webhook URL on PayOS Dashboard")
    print("   (See instructions above)")
    
    print("\n2. Test full payment flow:")
    print("   python test_full_flow.py")
    
    print("\n3. Monitor webhook:")
    print("   Watch Render logs in real-time")
    print("   https://dashboard.render.com  Logs")
    
    print("\n4. For more help:")
    print("   Read: SETUP_PAYOS_WEBHOOK.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

