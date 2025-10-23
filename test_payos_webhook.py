"""
Test PayOS Webhook - Script để test webhook locally và trên production
"""

import requests
import json
import datetime

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Chọn môi trường test
ENVIRONMENT = "production"  # "local" hoặc "production"

WEBHOOK_URLS = {
    "local": "http://127.0.0.1:5000/payos/webhook",
    "production": "https://ocr-uufr.onrender.com/payos/webhook"
}

WEBHOOK_URL = WEBHOOK_URLS[ENVIRONMENT]

# ==============================================================================
# TEST FUNCTIONS
# ==============================================================================

def test_1_get_verification():
    """Test 1: GET request - PayOS verification test"""
    print("\n" + "="*80)
    print("TEST 1: GET Verification (PayOS kiểm tra webhook URL)")
    print("="*80)
    
    try:
        response = requests.get(WEBHOOK_URL, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ PASS: Webhook URL is accessible")
            return True
        else:
            print("❌ FAIL: Unexpected status code")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_2_empty_post():
    """Test 2: POST with empty body - Test ping"""
    print("\n" + "="*80)
    print("TEST 2: POST Empty Body (Test ping)")
    print("="*80)
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json={},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ PASS: Empty POST handled correctly")
            return True
        else:
            print("❌ FAIL: Unexpected status code")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_3_successful_payment(order_id=None):
    """Test 3: POST with successful payment data"""
    print("\n" + "="*80)
    print("TEST 3: POST Successful Payment Data")
    print("="*80)
    
    # Nếu không có order_id, tạo mới
    if not order_id:
        order_id = int(datetime.datetime.now().timestamp() * 1000)
        print(f"⚠️  Using test order_id: {order_id}")
        print(f"   (Tạo order thật trước bằng /api/payment/create)")
    
    # Fake PayOS webhook payload (theo docs PayOS)
    webhook_data = {
        "code": "00",
        "desc": "success",
        "success": True,
        "data": {
            "orderCode": order_id,
            "amount": 100000,
            "description": "Test OCR Tool License",
            "accountNumber": "12345678",
            "reference": f"TEST{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "transactionDateTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "currency": "VND",
            "paymentLinkId": "test-payment-link-id-123",
            "code": "00",
            "desc": "Thành công"
        },
        "signature": "fake-signature-for-testing"
    }
    
    print(f"Payload:")
    print(json.dumps(webhook_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') or data.get('code') == '00':
                print("✅ PASS: Payment webhook processed successfully")
                
                # Hiển thị license key nếu có
                if 'data' in data and 'license_key' in data['data']:
                    print(f"\n🎉 LICENSE KEY: {data['data']['license_key']}")
                
                return True
            else:
                print("⚠️  WARNING: Response indicates failure")
                return False
        else:
            print("❌ FAIL: Unexpected status code")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_4_failed_payment():
    """Test 4: POST with failed payment data"""
    print("\n" + "="*80)
    print("TEST 4: POST Failed Payment Data")
    print("="*80)
    
    webhook_data = {
        "code": "99",
        "desc": "Payment failed",
        "success": False,
        "data": {
            "orderCode": 999999999,
            "amount": 100000
        }
    }
    
    print(f"Payload:")
    print(json.dumps(webhook_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ PASS: Failed payment handled correctly")
            return True
        else:
            print("❌ FAIL: Unexpected status code")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_5_health_check():
    """Test 5: Health check endpoint"""
    print("\n" + "="*80)
    print("TEST 5: Health Check Endpoint")
    print("="*80)
    
    health_url = WEBHOOK_URL.replace('/webhook', '/health')
    
    try:
        response = requests.get(health_url, timeout=10)
        
        print(f"URL: {health_url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ PASS: Health check OK")
            return True
        else:
            print("❌ FAIL: Health check failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_6_simulate_endpoint():
    """Test 6: Simulate endpoint (internal testing)"""
    print("\n" + "="*80)
    print("TEST 6: Simulate Endpoint (Internal Testing)")
    print("="*80)
    
    simulate_url = WEBHOOK_URL.replace('/webhook', '/simulate')
    
    test_data = {
        "orderCode": int(datetime.datetime.now().timestamp() * 1000),
        "amount": 100000,
        "description": "Test simulation"
    }
    
    print(f"URL: {simulate_url}")
    print(f"Payload: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            simulate_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ PASS: Simulate endpoint works")
            return True
        else:
            print("⚠️  WARNING: Simulate endpoint may not be available")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


# ==============================================================================
# MAIN TEST RUNNER
# ==============================================================================

def run_all_tests(order_id=None):
    """Chạy tất cả tests"""
    print("\n" + "="*80)
    print(f"🧪 PAYOS WEBHOOK TEST SUITE")
    print(f"Environment: {ENVIRONMENT.upper()}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print("="*80)
    
    results = {
        "Test 1 - GET Verification": test_1_get_verification(),
        "Test 2 - Empty POST": test_2_empty_post(),
        "Test 3 - Successful Payment": test_3_successful_payment(order_id),
        "Test 4 - Failed Payment": test_4_failed_payment(),
        "Test 5 - Health Check": test_5_health_check(),
        "Test 6 - Simulate Endpoint": test_6_simulate_endpoint()
    }
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*80 + "\n")
    
    return passed == total


# ==============================================================================
# USAGE EXAMPLES
# ==============================================================================

if __name__ == "__main__":
    import sys
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      PAYOS WEBHOOK TEST SCRIPT                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python test_payos_webhook.py                    # Run all tests
    python test_payos_webhook.py <order_id>         # Test with specific order_id
    
Examples:
    python test_payos_webhook.py
    python test_payos_webhook.py 1729685123456
    
Notes:
    - Test 3 cần order_id thật từ database
    - Tạo order bằng: POST /api/payment/create
    - Đổi ENVIRONMENT = "local" để test local server
    """)
    
    # Lấy order_id từ command line (nếu có)
    order_id = None
    if len(sys.argv) > 1:
        try:
            order_id = int(sys.argv[1])
            print(f"✓ Using order_id: {order_id}\n")
        except ValueError:
            print(f"⚠️  Invalid order_id: {sys.argv[1]}")
            print("   Using test order_id instead\n")
    
    # Chạy tests
    success = run_all_tests(order_id)
    
    # Exit code
    sys.exit(0 if success else 1)

