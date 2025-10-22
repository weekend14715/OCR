"""
Vietnamese OCR Tool - License Server
Backend API để quản lý và xác thực license keys
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import datetime
import uuid
from functools import wraps
import json
from payment_gateway import (
    VNPayPayment, MoMoPayment, ZaloPayPayment, VietQRPayment,
    generate_order_id, get_plan_info
)
# Import PayOS payment
try:
    from payos_handler import PAYOS_ENABLED, create_payment_link, verify_webhook_signature, get_payment_info
    if PAYOS_ENABLED:
        print("✅ PayOS Payment đã được kích hoạt!")
except ImportError:
    PAYOS_ENABLED = False
    print("⚠️  Warning: PayOS payment not available.")

# Import email sender
try:
    from email_sender import send_license_email
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False
    print("⚠️  Warning: Email sender not available. Emails will not be sent.")

app = Flask(__name__)
CORS(app)

# Cấu hình
DATABASE = 'licenses.db'

# PayOS Configuration (from environment variables)
import os
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', 'your-secure-admin-api-key-here-change-this')  # ⚠️ Đặt trong Render Environment Variables!
PAYOS_CLIENT_ID = os.getenv('PAYOS_CLIENT_ID', '')
PAYOS_API_KEY = os.getenv('PAYOS_API_KEY', '')
PAYOS_CHECKSUM_KEY = os.getenv('PAYOS_CHECKSUM_KEY', '')

# ==============================================================================
# DATABASE SETUP
# ==============================================================================

def init_db():
    """Khởi tạo database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Bảng licenses
    c.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE NOT NULL,
            email TEXT,
            machine_id TEXT,
            activation_date TEXT,
            expiry_date TEXT,
            plan_type TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            last_validated TEXT,
            order_id TEXT
        )
    ''')
    
    # Bảng orders (payment tracking)
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            plan_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            customer_email TEXT,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'pending',
            transaction_id TEXT,
            license_key TEXT,
            created_at TEXT NOT NULL,
            paid_at TEXT,
            expires_at TEXT
        )
    ''')
    
    # Bảng validation logs
    c.execute('''
        CREATE TABLE IF NOT EXISTS validation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT NOT NULL,
            machine_id TEXT,
            timestamp TEXT NOT NULL,
            success INTEGER NOT NULL,
            ip_address TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized")

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def generate_license_key():
    """Tạo license key ngẫu nhiên dạng XXXX-XXXX-XXXX-XXXX"""
    key = secrets.token_hex(8).upper()
    return f"{key[0:4]}-{key[4:8]}-{key[8:12]}-{key[12:16]}"

def hash_machine_id(machine_id):
    """Hash machine ID để bảo mật"""
    return hashlib.sha256(machine_id.encode()).hexdigest()

def get_machine_fingerprint():
    """Lấy hardware fingerprint (dùng cho demo)"""
    import platform
    import socket
    data = f"{platform.node()}-{platform.machine()}-{socket.gethostname()}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]

def require_admin_key(f):
    """Decorator kiểm tra admin API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-Admin-Key')
        if api_key != ADMIN_API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==============================================================================
# API ENDPOINTS - PUBLIC
# ==============================================================================

@app.route('/')
def index():
    """Trang chủ - Landing page bán license"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'service': 'OCR License Server',
        'timestamp': datetime.datetime.now().isoformat()
    }), 200

@app.route('/admin')
def admin():
    """Admin panel"""
    return render_template('admin.html')

@app.route('/api/validate', methods=['POST'])
def validate_license():
    """
    Xác thực license key
    POST: {
        "license_key": "XXXX-XXXX-XXXX-XXXX",
        "machine_id": "unique-machine-id"
    }
    """
    try:
        data = request.get_json()
        license_key = data.get('license_key', '').strip().upper()
        machine_id = data.get('machine_id', '').strip()
        
        if not license_key or not machine_id:
            return jsonify({
                'valid': False,
                'error': 'Missing license_key or machine_id'
            }), 400
        
        # Hash machine ID
        machine_hash = hash_machine_id(machine_id)
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Lấy thông tin license
        c.execute('''
            SELECT license_key, machine_id, activation_date, expiry_date, 
                   plan_type, is_active
            FROM licenses 
            WHERE license_key = ?
        ''', (license_key,))
        
        result = c.fetchone()
        
        # Log validation attempt
        ip_address = request.remote_addr
        timestamp = datetime.datetime.now().isoformat()
        
        if not result:
            # License không tồn tại
            c.execute('''
                INSERT INTO validation_logs 
                (license_key, machine_id, timestamp, success, ip_address)
                VALUES (?, ?, ?, 0, ?)
            ''', (license_key, machine_hash, timestamp, ip_address))
            conn.commit()
            conn.close()
            
            return jsonify({
                'valid': False,
                'error': 'Invalid license key'
            }), 200
        
        db_key, db_machine, activation_date, expiry_date, plan_type, is_active = result
        
        # Kiểm tra nếu license chưa được kích hoạt
        if not db_machine:
            # Kích hoạt lần đầu
            activation_date = datetime.datetime.now().isoformat()
            
            # Tính expiry date dựa vào plan
            if plan_type == 'lifetime':
                expiry_date = None
            elif plan_type == 'yearly':
                expiry_date = (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
            elif plan_type == 'monthly':
                expiry_date = (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
            
            c.execute('''
                UPDATE licenses 
                SET machine_id = ?, activation_date = ?, expiry_date = ?, last_validated = ?
                WHERE license_key = ?
            ''', (machine_hash, activation_date, expiry_date, timestamp, license_key))
            
            conn.commit()
            
            # Log success
            c.execute('''
                INSERT INTO validation_logs 
                (license_key, machine_id, timestamp, success, ip_address)
                VALUES (?, ?, ?, 1, ?)
            ''', (license_key, machine_hash, timestamp, ip_address))
            conn.commit()
            conn.close()
            
            return jsonify({
                'valid': True,
                'message': 'License activated successfully',
                'plan': plan_type,
                'activated': activation_date,
                'expires': expiry_date
            }), 200
        
        # Kiểm tra machine ID có khớp không
        if db_machine != machine_hash:
            c.execute('''
                INSERT INTO validation_logs 
                (license_key, machine_id, timestamp, success, ip_address)
                VALUES (?, ?, ?, 0, ?)
            ''', (license_key, machine_hash, timestamp, ip_address))
            conn.commit()
            conn.close()
            
            return jsonify({
                'valid': False,
                'error': 'License is already activated on another machine'
            }), 200
        
        # Kiểm tra active status
        if not is_active:
            conn.close()
            return jsonify({
                'valid': False,
                'error': 'License has been deactivated'
            }), 200
        
        # Kiểm tra expiry date
        if expiry_date:
            expiry_dt = datetime.datetime.fromisoformat(expiry_date)
            if datetime.datetime.now() > expiry_dt:
                conn.close()
                return jsonify({
                    'valid': False,
                    'error': 'License has expired',
                    'expired_date': expiry_date
                }), 200
        
        # Update last validated
        c.execute('''
            UPDATE licenses 
            SET last_validated = ?
            WHERE license_key = ?
        ''', (timestamp, license_key))
        
        # Log success
        c.execute('''
            INSERT INTO validation_logs 
            (license_key, machine_id, timestamp, success, ip_address)
            VALUES (?, ?, ?, 1, ?)
        ''', (license_key, machine_hash, timestamp, ip_address))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'valid': True,
            'plan': plan_type,
            'activated': activation_date,
            'expires': expiry_date,
            'message': 'License is valid'
        }), 200
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Server error: {str(e)}'
        }), 500

# ==============================================================================
# API ENDPOINTS - ADMIN (Yêu cầu X-Admin-Key header)
# ==============================================================================

@app.route('/api/admin/generate', methods=['POST'])
@require_admin_key
def admin_generate_license():
    """
    Tạo license key mới
    POST: {
        "plan_type": "lifetime|yearly|monthly",
        "quantity": 1,
        "email": "customer@example.com" (optional)
    }
    """
    try:
        data = request.get_json()
        plan_type = data.get('plan_type', 'lifetime')
        quantity = int(data.get('quantity', 1))
        email = data.get('email')
        
        if plan_type not in ['lifetime', 'yearly', 'monthly']:
            return jsonify({'error': 'Invalid plan_type'}), 400
        
        if quantity < 1 or quantity > 100:
            return jsonify({'error': 'Quantity must be between 1-100'}), 400
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        created_keys = []
        created_at = datetime.datetime.now().isoformat()
        
        for _ in range(quantity):
            license_key = generate_license_key()
            
            c.execute('''
                INSERT INTO licenses 
                (license_key, email, plan_type, created_at, is_active)
                VALUES (?, ?, ?, ?, 1)
            ''', (license_key, email, plan_type, created_at))
            
            created_keys.append(license_key)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'licenses': created_keys,
            'plan': plan_type,
            'quantity': quantity
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/licenses', methods=['GET'])
@require_admin_key
def admin_list_licenses():
    """Liệt kê tất cả licenses"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT license_key, email, machine_id, activation_date, 
                   expiry_date, plan_type, is_active, created_at, last_validated
            FROM licenses
            ORDER BY created_at DESC
        ''')
        
        licenses = []
        for row in c.fetchall():
            licenses.append({
                'license_key': row[0],
                'email': row[1],
                'machine_id': row[2][:16] + '...' if row[2] else None,
                'activation_date': row[3],
                'expiry_date': row[4],
                'plan_type': row[5],
                'is_active': bool(row[6]),
                'created_at': row[7],
                'last_validated': row[8]
            })
        
        conn.close()
        
        return jsonify({
            'licenses': licenses,
            'total': len(licenses)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/deactivate', methods=['POST'])
@require_admin_key
def admin_deactivate_license():
    """
    Vô hiệu hóa license
    POST: {"license_key": "XXXX-XXXX-XXXX-XXXX"}
    """
    try:
        data = request.get_json()
        license_key = data.get('license_key', '').strip().upper()
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            UPDATE licenses 
            SET is_active = 0
            WHERE license_key = ?
        ''', (license_key,))
        
        if c.rowcount == 0:
            conn.close()
            return jsonify({'error': 'License not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'License {license_key} deactivated'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
@require_admin_key
def admin_stats():
    """Thống kê licenses"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Tổng số licenses
        c.execute('SELECT COUNT(*) FROM licenses')
        total = c.fetchone()[0]
        
        # Số licenses đã kích hoạt
        c.execute('SELECT COUNT(*) FROM licenses WHERE machine_id IS NOT NULL')
        activated = c.fetchone()[0]
        
        # Số licenses còn hiệu lực
        c.execute('SELECT COUNT(*) FROM licenses WHERE is_active = 1')
        active = c.fetchone()[0]
        
        # Theo plan type
        c.execute('''
            SELECT plan_type, COUNT(*) 
            FROM licenses 
            GROUP BY plan_type
        ''')
        by_plan = {row[0]: row[1] for row in c.fetchall()}
        
        conn.close()
        
        return jsonify({
            'total_licenses': total,
            'activated': activated,
            'active': active,
            'by_plan': by_plan
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==============================================================================
# PAYMENT ENDPOINTS (AUTO LICENSE GENERATION) - LEGACY
# ==============================================================================

@app.route('/api/payment/create-legacy', methods=['POST'])
def create_payment_legacy():
    """
    [LEGACY] Tạo payment link cho VNPay/MoMo/ZaloPay
    POST Body: {
        "plan_type": "lifetime|yearly|monthly",
        "payment_method": "vnpay|momo|zalopay",
        "customer_email": "email@example.com"
    }
    """
    try:
        data = request.json
        plan_type = data.get('plan_type', '').lower()
        payment_method = data.get('payment_method', '').lower()
        customer_email = data.get('customer_email')
        
        # Validate plan
        plan_info = get_plan_info(plan_type)
        if not plan_info:
            return jsonify({'error': 'Invalid plan type'}), 400
        
        # Generate order ID
        order_id = generate_order_id()
        
        # Save order to database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO orders 
            (order_id, plan_type, amount, customer_email, payment_method, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            order_id,
            plan_type,
            plan_info['price'],
            customer_email,
            payment_method,
            datetime.datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Tạo payment URL
        order_info = f"License {plan_info['name']} - Vietnamese OCR Tool"
        payment_url = None
        
        if payment_method == 'vnpay':
            payment_url = VNPayPayment.create_payment_url(
                order_id=order_id,
                amount=plan_info['price'],
                order_info=order_info,
                customer_email=customer_email
            )
        elif payment_method == 'momo':
            success, result = MoMoPayment.create_payment(
                order_id=order_id,
                amount=plan_info['price'],
                order_info=order_info,
                customer_email=customer_email
            )
            if success:
                payment_url = result
            else:
                return jsonify({'error': result}), 400
                
        elif payment_method == 'zalopay':
            success, result = ZaloPayPayment.create_payment(
                order_id=order_id,
                amount=plan_info['price'],
                order_info=order_info,
                customer_email=customer_email
            )
            if success:
                payment_url = result
            else:
                return jsonify({'error': result}), 400
        else:
            return jsonify({'error': 'Invalid payment method'}), 400
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'payment_url': payment_url,
            'amount': plan_info['price'],
            'plan': plan_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/payment/vnpay/callback', methods=['GET'])
def vnpay_callback():
    """VNPay payment callback - Auto generate license"""
    try:
        params = dict(request.args)
        
        # Verify payment
        is_valid, transaction_info = VNPayPayment.verify_payment_response(params)
        
        if not is_valid or not transaction_info:
            return redirect(url_for('payment_failed'))
        
        order_id = transaction_info['order_id']
        
        # Generate license key
        license_key = auto_generate_license_for_order(
            order_id=order_id,
            payment_method='vnpay',
            transaction_id=transaction_info['transaction_no']
        )
        
        if license_key:
            return redirect(url_for('payment_success', license_key=license_key))
        else:
            return redirect(url_for('payment_failed'))
            
    except Exception as e:
        print(f"VNPay callback error: {e}")
        return redirect(url_for('payment_failed'))


@app.route('/api/payment/momo/callback', methods=['GET', 'POST'])
def momo_callback():
    """MoMo payment callback"""
    try:
        if request.method == 'POST':
            params = request.json
        else:
            params = dict(request.args)
        
        is_valid, transaction_info = MoMoPayment.verify_payment_response(params)
        
        if not is_valid or not transaction_info:
            return redirect(url_for('payment_failed'))
        
        order_id = transaction_info['order_id']
        
        license_key = auto_generate_license_for_order(
            order_id=order_id,
            payment_method='momo',
            transaction_id=transaction_info['transaction_no']
        )
        
        if license_key:
            return redirect(url_for('payment_success', license_key=license_key))
        else:
            return redirect(url_for('payment_failed'))
            
    except Exception as e:
        print(f"MoMo callback error: {e}")
        return redirect(url_for('payment_failed'))


@app.route('/api/payment/zalopay/callback', methods=['POST'])
def zalopay_callback():
    """ZaloPay payment callback"""
    try:
        callback_data = request.json
        
        is_valid, transaction_info = ZaloPayPayment.verify_callback(callback_data)
        
        if not is_valid or not transaction_info:
            return jsonify({'return_code': 0, 'return_message': 'Failed'})
        
        order_id = transaction_info['order_id']
        
        license_key = auto_generate_license_for_order(
            order_id=order_id,
            payment_method='zalopay',
            transaction_id=transaction_info['transaction_no']
        )
        
        if license_key:
            return jsonify({'return_code': 1, 'return_message': 'Success'})
        else:
            return jsonify({'return_code': 0, 'return_message': 'Failed'})
            
    except Exception as e:
        print(f"ZaloPay callback error: {e}")
        return jsonify({'return_code': 0, 'return_message': str(e)})


def auto_generate_license_for_order(order_id, payment_method, transaction_id):
    """
    Tự động tạo license key sau khi thanh toán thành công
    Returns: license_key or None
    """
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Get order info
        c.execute('SELECT plan_type, customer_email FROM orders WHERE order_id = ?', (order_id,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return None
        
        plan_type, customer_email = row
        
        # Check if license already generated
        c.execute('SELECT license_key FROM orders WHERE order_id = ? AND license_key IS NOT NULL', (order_id,))
        existing = c.fetchone()
        if existing:
            conn.close()
            return existing[0]  # Return existing license
        
        # Generate new license key
        license_key = generate_license_key()
        created_at = datetime.datetime.now().isoformat()
        
        # Calculate expiry date based on plan
        plan_info = get_plan_info(plan_type)
        if plan_info['duration_days'] >= 36500:  # Lifetime
            expiry_date = None
        else:
            expiry = datetime.datetime.now() + datetime.timedelta(days=plan_info['duration_days'])
            expiry_date = expiry.isoformat()
        
        # Insert license
        c.execute('''
            INSERT INTO licenses 
            (license_key, email, plan_type, created_at, is_active, order_id)
            VALUES (?, ?, ?, ?, 1, ?)
        ''', (license_key, customer_email, plan_type, created_at, order_id))
        
        # Update order
        c.execute('''
            UPDATE orders 
            SET payment_status = 'completed',
                transaction_id = ?,
                license_key = ?,
                paid_at = ?,
                expires_at = ?
            WHERE order_id = ?
        ''', (transaction_id, license_key, created_at, expiry_date, order_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Auto-generated license: {license_key} for order: {order_id}")
        
        # Gửi email license key cho khách hàng
        if EMAIL_ENABLED and customer_email:
            try:
                result = send_license_email(
                    to_email=customer_email,
                    license_key=license_key,
                    customer_name=customer_email.split('@')[0],  # Lấy tên từ email
                    order_id=order_id,
                    plan_type=plan_type
                )
                
                if result['success']:
                    print(f"✅ Email sent to {customer_email} via {result['account_used']}")
                else:
                    print(f"❌ Failed to send email: {result['message']}")
            except Exception as e:
                print(f"❌ Email error: {e}")
        
        return license_key
        
    except Exception as e:
        print(f"Error generating license: {e}")
        return None


@app.route('/success')
def payment_success():
    """Payment success page - Show license key"""
    license_key = request.args.get('license_key')
    return render_template('success.html', license_key=license_key)


@app.route('/failed')
def payment_failed():
    """Payment failed page"""
    return render_template('failed.html')


@app.route('/api/order/status/<order_id>', methods=['GET'])
def get_order_status(order_id):
    """Check order status and get license if paid"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT order_id, plan_type, amount, payment_status, 
                   license_key, created_at, paid_at
            FROM orders
            WHERE order_id = ?
        ''', (order_id,))
        
        row = c.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({
            'order_id': row[0],
            'plan_type': row[1],
            'amount': row[2],
            'payment_status': row[3],
            'license_key': row[4],
            'created_at': row[5],
            'paid_at': row[6]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==============================================================================
# PAYOS PAYMENT INTEGRATION
# ==============================================================================

@app.route('/api/payment/create-order', methods=['POST'])
def create_payment_order():
    """
    Tạo đơn hàng mới và lấy thông tin chuyển khoản + VietQR
    POST: {
        "customer_email": "email@example.com",
        "plan_type": "lifetime",
        "amount": 100000
    }
    """
    try:
        data = request.get_json()
        customer_email = data.get('customer_email', '').strip()
        plan_type = data.get('plan_type', 'lifetime')
        amount = int(data.get('amount', 100000))
        
        if not customer_email or '@' not in customer_email:
            return jsonify({'error': 'Invalid email'}), 400
        
        # Tạo order ID
        order_id = generate_order_id()
        created_at = datetime.datetime.now().isoformat()
        
        # Lưu order vào database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO orders 
            (order_id, plan_type, amount, customer_email, payment_method, payment_status, created_at)
            VALUES (?, ?, ?, ?, 'bank_transfer', 'pending', ?)
        ''', (order_id, plan_type, amount, customer_email, created_at))
        
        conn.commit()
        conn.close()
        
        # Lấy thông tin bank (giữ cho legacy VietQR support)
        bank_info = VietQRPayment.get_bank_info()
        
        # Tạo VietQR URL
        vietqr_url = VietQRPayment.generate_vietqr_url(
            bank_code=bank_info['bank_code'],
            account_number=bank_info['account_number'],
            account_name=bank_info['account_name'],
            amount=amount,
            description=customer_email
        )
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'bank_info': bank_info,
            'amount': amount,
            'transfer_content': customer_email,
            'vietqr_url': vietqr_url
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/payment/create', methods=['POST'])
def create_payos_payment():
    """
    Tạo QR code thanh toán PayOS
    
    POST: {
        "email": "customer@example.com",
        "plan_type": "lifetime",  # hoặc "trial"
        "amount": 100000
    }
    
    Response: {
        "success": true,
        "order_id": "...",
        "checkout_url": "https://...",
        "qr_code": "https://..."
    }
    """
    try:
        if not PAYOS_ENABLED:
            return jsonify({'error': 'PayOS not configured'}), 503
        
        data = request.get_json()
        customer_email = data.get('email', '').strip().lower()
        plan_type = data.get('plan_type', 'lifetime')
        amount = int(data.get('amount', 100000))
        
        if not customer_email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Validate email
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(email_pattern, customer_email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Tạo order
        order_id = int(datetime.datetime.now().timestamp() * 1000)  # PayOS yêu cầu số nguyên
        created_at = datetime.datetime.now().isoformat()
        
        # Lưu order vào DB
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO orders 
            (order_id, plan_type, amount, customer_email, payment_method, payment_status, created_at)
            VALUES (?, ?, ?, ?, 'payos', 'pending', ?)
        ''', (str(order_id), plan_type, amount, customer_email, created_at))
        
        conn.commit()
        conn.close()
        
        # Tạo payment link với PayOS
        description = f"OCR Tool {plan_type} - {customer_email}"
        result = create_payment_link(
            order_id=order_id,
            amount=amount,
            description=description,
            customer_email=customer_email,
            return_url=f"https://your-app.com/payment/success?order_id={order_id}",
            cancel_url=f"https://your-app.com/payment/cancel?order_id={order_id}"
        )
        
        if result.get('success'):
            print(f"✅ Created PayOS payment link for {customer_email}")
            print(f"   Order ID: {order_id}")
            print(f"   Amount: {amount} VND")
            
            return jsonify({
                'success': True,
                'order_id': str(order_id),
                'checkout_url': result['checkout_url'],
                'qr_code': result['qr_code'],
                'amount': amount,
                'plan_type': plan_type
            }), 200
        else:
            return jsonify({'error': result.get('error', 'Failed to create payment link')}), 500
        
    except Exception as e:
        print(f"❌ Error creating payment: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/webhook/payos', methods=['POST'])
def payos_webhook():
    """
    Webhook nhận thông báo từ PayOS khi thanh toán thành công
    
    PayOS sẽ gửi POST request với data:
    {
        "code": "00",
        "desc": "success",
        "data": {
            "orderCode": 123456789,
            "amount": 100000,
            "description": "...",
            "accountNumber": "...",
            "reference": "...",
            "transactionDateTime": "...",
            ...
        },
        "signature": "..."
    }
    """
    try:
        # Lấy data từ webhook
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data'}), 400
        
        print(f"📩 Received PayOS webhook: {data}")
        
        # Lấy signature từ header hoặc data
        signature = request.headers.get('x-signature') or data.get('signature')
        
        # TODO: Verify signature (TẠM THỜI TẮT ĐỂ TEST)
        # PayOS webhook signature verification sẽ được thêm sau
        print(f"📝 Signature received: {signature}")
        
        # Parse payment info
        payment_data = data.get('data', {})
        code = data.get('code')
        
        # Kiểm tra thanh toán thành công
        if code != '00':
            print(f"⚠️ Payment not successful: {code}")
            return jsonify({'error': 'Payment not successful'}), 400
        
        order_code = payment_data.get('orderCode')
        amount = int(payment_data.get('amount', 0))
        transaction_ref = payment_data.get('reference', '')
        
        if not order_code:
            return jsonify({'error': 'No order code'}), 400
        
        # Tìm order
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT order_id, customer_email, plan_type, payment_status 
            FROM orders 
            WHERE order_id = ?
        ''', (str(order_code),))
        
        order = c.fetchone()
        
        if not order:
            print(f"⚠️ Order not found: {order_code}")
            conn.close()
            return jsonify({'error': 'Order not found'}), 404
        
        order_id, customer_email, plan_type, payment_status = order
        
        # Kiểm tra đã thanh toán chưa
        if payment_status == 'completed':
            print(f"⚠️ Order already completed: {order_id}")
            conn.close()
            return jsonify({'success': True, 'message': 'Already processed'}), 200
        
        conn.close()
        
        # Tự động tạo license key
        license_key = auto_generate_license(order_id, plan_type, customer_email, transaction_ref)
        
        if license_key:
            print(f"✅ Successfully processed PayOS payment: {order_code}")
            print(f"   Email: {customer_email}")
            print(f"   License: {license_key}")
            
            return jsonify({
                'success': True,
                'order_id': order_id,
                'license_key': license_key
            }), 200
        else:
            return jsonify({'error': 'Failed to generate license'}), 500
        
    except Exception as e:
        print(f"❌ PayOS webhook error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/payos/test-webhook', methods=['POST'])
@require_admin_key
def test_payos_webhook():
    """
    Test endpoint để test PayOS webhook manually
    POST: {
        "order_id": "123456789",
        "amount": 100000
    }
    """
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        amount = data.get('amount', 100000)
        
        if not order_id:
            return jsonify({'error': 'order_id is required'}), 400
        
        # Simulate webhook data
        webhook_data = {
            'code': '00',
            'desc': 'success',
            'data': {
                'orderCode': int(order_id),
                'amount': amount,
                'description': 'Test payment',
                'reference': 'TEST' + str(int(datetime.datetime.now().timestamp())),
                'transactionDateTime': datetime.datetime.now().isoformat()
            }
        }
        
        # Call webhook handler
        with app.test_client() as client:
            response = client.post('/api/webhook/payos', 
                                 json=webhook_data,
                                 content_type='application/json')
            
            return response.get_json(), response.status_code
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("🚀 Vietnamese OCR Tool - License Server")
    print("="*60)
    print(f"📡 Server running on: http://127.0.0.1:5000")
    print(f"🔑 Admin API Key: {ADMIN_API_KEY}")
    print("\n⚠️  IMPORTANT: Change ADMIN_API_KEY in production!")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

