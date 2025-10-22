"""Test VietQR API"""

import requests
import json

# Test API endpoint
url = "http://localhost:5000/api/payment/create-order"

data = {
    "customer_email": "hoangtuan.th484@gmail.com",
    "plan_type": "lifetime",
    "amount": 100000
}

print("Testing VietQR API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")
print("\nSending request...")

try:
    response = requests.post(url, json=data)
    result = response.json()
    
    print(f"\nStatus: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get('success') and result.get('vietqr_url'):
        print(f"\n=== SUCCESS ===")
        print(f"VietQR URL: {result['vietqr_url']}")
        print(f"\nCopy URL tren vao browser de xem QR code!")
    else:
        print("\n=== FAILED ===")
        
except requests.exceptions.ConnectionError:
    print("\n ERROR: Cannot connect to server!")
    print("Please start server first: python license_server/app.py")
except Exception as e:
    print(f"\n ERROR: {e}")

