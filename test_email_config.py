#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Email Configuration - Kiểm tra 2 tài khoản Gmail
"""

import sys
import os

# Add license_server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'license_server'))

from license_server.email_sender import LicenseEmailSender


def test_email_accounts():
    """
    Test gửi email từ 2 tài khoản
    """
    
    print("\n" + "="*70)
    print("🧪 TEST HỆ THỐNG EMAIL - OCR TOOL LICENSE")
    print("="*70)
    
    sender = LicenseEmailSender()
    
    # Xem thông tin accounts
    from license_server.email_config import EMAIL_ACCOUNTS
    
    print(f"\n📧 Đã load {len(EMAIL_ACCOUNTS)} tài khoản:")
    for i, acc in enumerate(EMAIL_ACCOUNTS, 1):
        print(f"  {i}. {acc['email']} (Limit: {acc['daily_limit']} emails/day)")
    
    print("\n" + "─"*70)
    
    # Nhập email nhận
    receiver = input("\n📩 Nhập email nhận (để test): ").strip()
    
    if not receiver:
        print("\n❌ Email không hợp lệ!")
        return
    
    # Xác nhận
    print(f"\n⚠️  Sắp gửi email test đến: {receiver}")
    confirm = input("Tiếp tục? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("\n❌ Đã hủy!")
        return
    
    # Gửi email test
    print("\n" + "="*70)
    print("📤 ĐANG GỬI EMAIL TEST...")
    print("="*70 + "\n")
    
    result = sender.send_license_key(
        to_email=receiver,
        license_key="TEST-ABCD-1234-EFGH",
        customer_name="Người dùng Test",
        order_id="TEST-ORDER-20250101",
        plan_type="lifetime"
    )
    
    # Hiển thị kết quả
    print("\n" + "="*70)
    if result['success']:
        print("✅ THÀNH CÔNG!")
        print("="*70)
        print(f"Tài khoản sử dụng: {result['account_used']}")
        print(f"Đã gửi hôm nay: {result['emails_sent_today']}")
        print(f"Còn lại hôm nay: {result['emails_remaining']}")
        print(f"\n📬 Check email của bạn: {receiver}")
        print("   (Check cả Spam/Junk nếu không thấy)")
    else:
        print("❌ THẤT BẠI!")
        print("="*70)
        print(f"Lỗi: {result['message']}")
        print(f"Tài khoản: {result['account_used']}")
    print("="*70 + "\n")
    
    # Hiển thị trạng thái
    print("\n📊 TRẠNG THÁI HỆ THỐNG:")
    print("─"*70)
    status = sender.get_status()
    
    for i, acc in enumerate(status['accounts'], 1):
        print(f"\nTài khoản {i}: {acc['email']}")
        print(f"  Đã gửi: {acc['sent_today']}/{acc['limit']}")
        print(f"  Còn lại: {acc['remaining']}")
    
    print(f"\nTổng: {status['total_sent']}/{status['total_limit']} emails")
    print("─"*70)


def test_multiple_sends():
    """
    Test gửi nhiều email để kiểm tra chuyển đổi account
    """
    
    print("\n" + "="*70)
    print("🔄 TEST GỬI NHIỀU EMAIL (Kiểm tra auto-switch)")
    print("="*70)
    
    sender = LicenseEmailSender()
    
    receiver = input("\nNhập email nhận: ").strip()
    count = input("Số lượng email (2-5): ").strip()
    
    try:
        count = int(count)
        if count < 2 or count > 5:
            print("❌ Số lượng phải từ 2-5!")
            return
    except:
        print("❌ Số lượng không hợp lệ!")
        return
    
    print(f"\n⚠️  Sẽ gửi {count} emails đến {receiver}")
    confirm = input("Tiếp tục? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("\n❌ Đã hủy!")
        return
    
    # Gửi nhiều emails
    print("\n" + "="*70)
    print(f"📤 ĐANG GỬI {count} EMAILS...")
    print("="*70 + "\n")
    
    for i in range(count):
        print(f"Email {i+1}/{count}...", end=" ")
        
        result = sender.send_license_key(
            to_email=receiver,
            license_key=f"TEST-{i+1:04d}-ABCD-EFGH",
            customer_name=f"Test User #{i+1}",
            order_id=f"TEST-ORDER-{i+1:04d}",
            plan_type="lifetime"
        )
        
        if result['success']:
            print(f"✅ Từ {result['account_used']}")
        else:
            print(f"❌ {result['message']}")
    
    # Trạng thái sau khi gửi
    print("\n" + "="*70)
    print("📊 TRẠNG THÁI SAU KHI GỬI")
    print("="*70)
    
    status = sender.get_status()
    for i, acc in enumerate(status['accounts'], 1):
        print(f"\nTài khoản {i}: {acc['email']}")
        print(f"  Đã gửi: {acc['sent_today']}/{acc['limit']}")
        print(f"  Còn lại: {acc['remaining']}")
    
    print(f"\nTổng: {status['total_sent']}/{status['total_limit']} emails")
    print("="*70 + "\n")


if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║      🧪 TEST EMAIL CONFIGURATION - OCR TOOL                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Chức năng:
  1. Test gửi 1 email
  2. Test gửi nhiều emails (kiểm tra auto-switch)
  3. Xem trạng thái
  4. Thoát
""")
    
    while True:
        choice = input("\nChọn (1-4): ").strip()
        
        if choice == '1':
            test_email_accounts()
            
        elif choice == '2':
            test_multiple_sends()
            
        elif choice == '3':
            sender = LicenseEmailSender()
            status = sender.get_status()
            
            print("\n" + "="*70)
            print(f"📊 TRẠNG THÁI HỆ THỐNG - {status['date']}")
            print("="*70)
            
            for i, acc in enumerate(status['accounts'], 1):
                print(f"\nTài khoản {i}: {acc['email']}")
                print(f"  Đã gửi: {acc['sent_today']}/{acc['limit']}")
                print(f"  Còn lại: {acc['remaining']}")
                print(f"  Sử dụng: {acc['percentage_used']:.1f}%")
            
            print(f"\nTổng: {status['total_sent']}/{status['total_limit']} emails")
            print(f"Còn lại: {status['total_remaining']} emails")
            print("="*70)
            
        elif choice == '4':
            print("\n👋 Tạm biệt!\n")
            break
            
        else:
            print("\n❌ Lựa chọn không hợp lệ!")

