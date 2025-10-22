#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Script - Gửi Email License Key
"""

import sys
import os
import uuid

# Add license_server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'license_server'))

from email_sender import send_license_email

def test_send_email():
    """Test gửi email với Gmail thật"""
    
    print("\n" + "="*70)
    print("🧪 TEST SEND EMAIL WITH REAL GMAIL ACCOUNTS")
    print("="*70)
    
    # Generate test license key
    license_key = f"TEST-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"
    
    # Test data
    test_data = {
        'to_email': 'hoangtuan.th484@gmail.com',  # Email nhận (của bạn)
        'license_key': license_key,
        'customer_name': 'Hoang Tuan (Test)',
        'plan_type': 'lifetime'
    }
    
    print(f"\n📧 Sending test email...")
    print(f"   To: {test_data['to_email']}")
    print(f"   License: {test_data['license_key']}")
    print(f"   Customer: {test_data['customer_name']}")
    print(f"   Plan: {test_data['plan_type']}")
    print()
    
    # Send email
    result = send_license_email(
        to_email=test_data['to_email'],
        license_key=test_data['license_key'],
        customer_name=test_data['customer_name'],
        plan_type=test_data['plan_type']
    )
    
    # Print result
    print("\n" + "="*70)
    print("📊 RESULT:")
    print("="*70)
    
    if result['success']:
        print(f"✅ Success: {result['success']}")
        print(f"📧 Message: {result['message']}")
        print(f"🔑 Account Used: {result['account_used']}")
        print()
        print("🎉 Email sent successfully!")
        print(f"📬 Check your inbox: {test_data['to_email']}")
    else:
        print(f"❌ Failed: {result['message']}")
    
    print("="*70)
    print()
    
    return result

if __name__ == '__main__':
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    test_send_email()

