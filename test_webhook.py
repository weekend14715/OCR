#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test PayOS Payment và Webhook
"""
import sys
import io
import requests
import json

# Fix encoding trên Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API endpoint
API_URL = "https://ocr-uufr.onrender.com"

print("\n" + "="*60)
print("🧪 TEST PAYOS PAYMENT VÀ WEBHOOK")
print("="*60 + "\n")

# 1. Test webhook endpoint (GET)
print("1️⃣ Test webhook endpoint...")
try:
    response = requests.get(f"{API_URL}/api/webhook/payos", timeout=10)
    print(f"   ✅ Webhook ready: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# 2. Tạo payment
print("2️⃣ Tạo payment test...")
try:
    response = requests.post(
        f"{API_URL}/api/payment/create",
        json={
            "email": "test@example.com",
            "plan": "yearly",
            "amount": 500000
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Payment created!")
        print(f"   📦 Order Code: {data.get('order_code')}")
        print(f"   💰 Amount: {data.get('amount'):,} VND")
        print(f"   🔗 QR Code: {data.get('qr_code_url')}")
        print(f"\n   👉 Mở link này để thanh toán:")
        print(f"      {data.get('checkout_url')}")
    else:
        print(f"   ❌ Error: {response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("📝 HƯỚNG DẪN:")
print("="*60)
print("1. Copy link checkout_url ở trên")
print("2. Mở trong trình duyệt")
print("3. Quét QR code bằng app ngân hàng")
print("4. Sau khi thanh toán:")
print("   - PayOS gọi webhook")
print("   - Server tạo license")
print("   - Email tự động gửi")
print("="*60 + "\n")

