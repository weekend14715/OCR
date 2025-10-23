#!/usr/bin/env python3
"""
Test PayOS SDK để tìm đúng method name
"""

import os
from dotenv import load_dotenv

# Load env
load_dotenv('license_server/.env')

try:
    from payos import PayOS
    
    client_id = os.getenv('PAYOS_CLIENT_ID')
    api_key = os.getenv('PAYOS_API_KEY')
    checksum_key = os.getenv('PAYOS_CHECKSUM_KEY')
    
    print("Initializing PayOS client...")
    payos = PayOS(
        client_id=client_id,
        api_key=api_key,
        checksum_key=checksum_key
    )
    
    print("PayOS initialized!")
    print("\nAll methods available:")
    methods = [m for m in dir(payos) if not m.startswith('_')]
    for m in methods:
        print(f"   - {m}")
    
    print("\nLooking for payment creation methods:")
    payment_methods = [m for m in methods if 'payment' in m.lower() or 'link' in m.lower() or 'create' in m.lower()]
    for m in payment_methods:
        print(f"   * {m}")
    
    # Try to create a test payment
    print("\nTesting payment creation...")
    payment_data = {
        "orderCode": 123456,
        "amount": 10000,
        "description": "Test payment",
        "returnUrl": "https://test.com/success",
        "cancelUrl": "https://test.com/cancel"
    }
    
    for method_name in ['createPaymentLink', 'create_payment_link', 'create_link', 'createLink']:
        if hasattr(payos, method_name):
            print(f"\nFound method: {method_name}")
            print(f"   Trying to call it...")
            try:
                method = getattr(payos, method_name)
                result = method(payment_data)
                print(f"   SUCCESS!")
                print(f"   Result type: {type(result)}")
                print(f"   Result: {result}")
                break
            except Exception as e:
                print(f"   Error: {e}")
        else:
            print(f"   Method '{method_name}' not found")

except ImportError:
    print("PayOS SDK not installed. Install: pip install payos")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

