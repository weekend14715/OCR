#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Environment Variables - Debug Tool
Kiểm tra xem biến EMAIL_ACCOUNTS có load được không
"""

import os
import json

print("="*70)
print("🔍 KIỂM TRA BIẾN MÔI TRƯỜNG EMAIL_ACCOUNTS")
print("="*70)

# Kiểm tra biến có tồn tại không
email_accounts_env = os.getenv('EMAIL_ACCOUNTS')

if not email_accounts_env:
    print("❌ KHÔNG TÌM THẤY biến EMAIL_ACCOUNTS")
    print("\nHướng dẫn:")
    print("1. Vào Render Dashboard → Environment")
    print("2. Thêm biến EMAIL_ACCOUNTS")
    print("3. Giá trị: [{'email':'...','password':'...','daily_limit':500}]")
else:
    print("✅ TÌM THẤY biến EMAIL_ACCOUNTS")
    print(f"\n📏 Độ dài: {len(email_accounts_env)} ký tự")
    print(f"\n📄 Giá trị (50 ký tự đầu):")
    print(f"   {email_accounts_env[:50]}...")
    
    # Thử parse JSON
    try:
        accounts = json.loads(email_accounts_env)
        print(f"\n✅ PARSE JSON THÀNH CÔNG!")
        print(f"   Số lượng accounts: {len(accounts)}")
        
        for i, acc in enumerate(accounts, 1):
            print(f"\n   Account {i}:")
            print(f"   - Email: {acc.get('email', 'MISSING')}")
            print(f"   - Password: {'***' if acc.get('password') else 'MISSING'}")
            print(f"   - Daily Limit: {acc.get('daily_limit', 'MISSING')}")
        
        print("\n" + "="*70)
        print("🎉 EMAIL CONFIG SẼ HOẠT ĐỘNG!")
        print("="*70)
        
    except json.JSONDecodeError as e:
        print(f"\n❌ LỖI PARSE JSON!")
        print(f"   Error: {e}")
        print("\n🔧 Kiểm tra lại format:")
        print('   - Phải dùng dấu " thay vì \'')
        print("   - Không có khoảng trắng thừa")
        print("   - Đúng cú pháp JSON")
        print("\n📋 Format đúng:")
        print('   [{"email":"...","password":"...","daily_limit":500}]')

print("\n")

