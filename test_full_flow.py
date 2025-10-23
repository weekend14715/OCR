#!/usr/bin/env python3
"""
Test full payment flow với PayOS webhook
"""
import requests
import time
import json
from datetime import datetime

# Config
SERVER_URL = "https://license-server-hjat.onrender.com"
TEST_MACHINE_ID = f"TEST-{int(time.time())}"
TEST_EMAIL = "test@example.com"

def print_step(step, message):
    print(f"\n{'='*60}")
    print(f"{step} {message}")
    print(f"{'='*60}\n")

def check_server_health():
    """Kiểm tra server có sẵn sàng không"""
    print("🔍 Checking server health...")
    try:
        response = requests.get(f"{SERVER_URL}/payos/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy: {data}")
            return True
        else:
            print(f"⚠️ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach server: {e}")
        return False

def create_payment():
    """Tạo payment mới"""
    print_step("1️⃣", "CREATING PAYMENT")
    
    payload = {
        "machine_id": TEST_MACHINE_ID,
        "amount": 200000,
        "months": 1,
        "customer_email": TEST_EMAIL,
        "customer_name": "Test User"
    }
    
    print(f"Request payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f"{SERVER_URL}/payos/create-payment",
            json=payload,
            timeout=30
        )
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Payment created successfully!")
            print(f"\n📋 Payment Details:")
            print(f"   Order ID: {data.get('order_id')}")
            print(f"   Amount: {data.get('amount'):,}đ")
            print(f"   QR Code: {data.get('qr_code_url')}")
            print(f"\n🔗 Checkout URL:")
            print(f"   {data.get('checkout_url')}")
            
            return data.get('order_id'), data.get('checkout_url')
        else:
            error = response.json()
            print(f"❌ Failed to create payment:")
            print(json.dumps(error, indent=2, ensure_ascii=False))
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def wait_for_webhook(order_id, timeout_minutes=5):
    """Đợi webhook từ PayOS"""
    print_step("2️⃣", "WAITING FOR WEBHOOK")
    
    print(f"⏳ Please scan QR code and complete payment...")
    print(f"   Machine ID: {TEST_MACHINE_ID}")
    print(f"   Order ID: {order_id}")
    print(f"   Timeout: {timeout_minutes} minutes\n")
    
    timeout_seconds = timeout_minutes * 60
    check_interval = 10  # Check every 10 seconds
    checks = timeout_seconds // check_interval
    
    for i in range(checks):
        elapsed = (i + 1) * check_interval
        minutes = elapsed // 60
        seconds = elapsed % 60
        
        print(f"   [{elapsed}s] Checking license status... ({i+1}/{checks})")
        
        try:
            response = requests.get(
                f"{SERVER_URL}/license/check",
                params={"machine_id": TEST_MACHINE_ID},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid"):
                    print(f"\n✅ License created!")
                    return True, data
                    
        except Exception as e:
            print(f"   ⚠️ Check failed: {e}")
        
        if i < checks - 1:  # Don't sleep on last iteration
            time.sleep(check_interval)
    
    print(f"\n❌ Timeout - No webhook received after {timeout_minutes} minutes")
    return False, None

def verify_license(license_data):
    """Hiển thị thông tin license"""
    print_step("3️⃣", "LICENSE VERIFICATION")
    
    print(f"License Details:")
    print(json.dumps(license_data, indent=2, ensure_ascii=False))
    
    if license_data.get("valid"):
        print(f"\n✅ License is valid!")
        print(f"   Machine ID: {license_data.get('machine_id')}")
        print(f"   Valid Until: {license_data.get('valid_until')}")
        print(f"   Days Left: {license_data.get('days_left')}")
        return True
    else:
        print(f"\n❌ License is invalid")
        return False

def check_webhook_logs():
    """Hướng dẫn kiểm tra logs"""
    print_step("📊", "HOW TO CHECK WEBHOOK LOGS")
    
    print(f"1. Render Dashboard:")
    print(f"   https://dashboard.render.com")
    print(f"   → Select: license-server-hjat")
    print(f"   → Click: Logs tab")
    print(f"   → Search: '[WEBHOOK] Received PayOS webhook'")
    
    print(f"\n2. PayOS Dashboard:")
    print(f"   https://my.payos.vn/")
    print(f"   → Menu: Webhook Logs")
    print(f"   → Check status: 200 OK = success")
    
    print(f"\n3. Manual webhook test:")
    print(f"   curl -X POST {SERVER_URL}/payos/webhook \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"code\": \"00\", \"data\": {{\"orderCode\": \"TEST\"}}}}'")

def main():
    print(f"\n{'#'*60}")
    print(f"# 🧪 TEST FULL PAYMENT FLOW WITH WEBHOOK")
    print(f"{'#'*60}")
    print(f"\nServer: {SERVER_URL}")
    print(f"Machine ID: {TEST_MACHINE_ID}")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 0: Check server health
    if not check_server_health():
        print("\n❌ Server is not healthy. Please check Render deployment.")
        print("   Try: curl https://license-server-hjat.onrender.com/payos/health")
        return
    
    # Step 1: Create payment
    order_id, checkout_url = create_payment()
    if not order_id:
        print("\n❌ Cannot create payment. Test aborted.")
        return
    
    print(f"\n{'='*60}")
    print(f"⚠️  IMPORTANT: PLEASE COMPLETE PAYMENT NOW!")
    print(f"{'='*60}")
    print(f"\nOpen this URL in your browser:")
    print(f"\n🔗 {checkout_url}\n")
    print(f"Then scan QR code with your banking app to pay 200,000đ")
    print(f"\nI will wait for webhook notification...")
    
    # Step 2: Wait for webhook
    success, license_data = wait_for_webhook(order_id, timeout_minutes=5)
    
    if not success:
        print("\n⚠️ Webhook was not received. Possible reasons:")
        print("   1. Payment not completed yet")
        print("   2. Webhook URL not configured on PayOS Dashboard")
        print("   3. Server error handling webhook")
        print("   4. PayOS webhook delay (rare)")
        check_webhook_logs()
        return
    
    # Step 3: Verify license
    if verify_license(license_data):
        print(f"\n{'='*60}")
        print(f"🎉 TEST PASSED - FULL FLOW WORKING!")
        print(f"{'='*60}")
        print(f"\n✅ Payment → Webhook → License creation → Success!")
        print(f"\nNext steps:")
        print(f"   1. Check email '{TEST_EMAIL}' for license")
        print(f"   2. Test from your actual application")
        print(f"   3. Configure webhook URL on PayOS Dashboard")
    else:
        print(f"\n❌ License verification failed")
        check_webhook_logs()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

