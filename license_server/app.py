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
import hmac
import time
from payment_gateway import (
    VNPayPayment, MoMoPayment, ZaloPayPayment, VietQRPayment,
    generate_order_id, get_plan_info
)
# Import PayOS payment
try:
    from payos_handler import PAYOS_ENABLED, create_payment_link
    from payos_handler import app as payos_app  # Import Flask Blueprint
    if PAYOS_ENABLED:
        print("PayOS Payment activated successfully!")
except ImportError:
    PAYOS_ENABLED = False
    payos_app = None
    print("Warning: PayOS payment not available.")

# Import email sender
try:
    from email_sender import send_license_email
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False
    print("Warning: Email sender not available. Emails will not be sent.")

app = Flask(__name__)
CORS(app)

# Register PayOS Blueprint
if payos_app:
    app.register_blueprint(payos_app, url_prefix='/payos')
    print("PayOS Blueprint registered at /payos/*")

# Cấu hình
import os

# Database configuration - use persistent disk on Render, local file in dev
PERSISTENT_DIR = '/var/data'  # Render Disk mount path
if os.path.exists(PERSISTENT_DIR) and os.access(PERSISTENT_DIR, os.W_OK):
    DATABASE = os.path.join(PERSISTENT_DIR, 'licenses.db')
    print(f"[CONFIG] 💾 Using persistent storage: {DATABASE}")
else:
    DATABASE = 'licenses.db'
    print(f"[CONFIG] [FOLDER] Using local storage: {DATABASE}")

# PayOS Configuration (from environment variables)
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', 'your-secure-admin-api-key-here-change-this')  # [WARNING] Đặt trong Render Environment Variables!
PAYOS_CLIENT_ID = os.getenv('PAYOS_CLIENT_ID', '')
PAYOS_API_KEY = os.getenv('PAYOS_API_KEY', '')
PAYOS_CHECKSUM_KEY = os.getenv('PAYOS_CHECKSUM_KEY', '')

# ==============================================================================
# HELPER FUNCTIONS - TIMEZONE
# ==============================================================================

def get_vietnam_time():
    """Lấy thời gian hiện tại theo múi giờ +7 (Việt Nam)"""
    vietnam_tz = datetime.timezone(datetime.timedelta(hours=7))
    return datetime.datetime.now(vietnam_tz)

def get_vietnam_isoformat():
    """Lấy thời gian hiện tại theo múi giờ +7 ở định dạng ISO"""
    return get_vietnam_time().isoformat()

# ==============================================================================
# DATABASE SETUP
# ==============================================================================

def init_db():
    """Khởi tạo database"""
    print(f"[INIT-DB] [TOOL] Initializing database at: {DATABASE}")
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
            status TEXT DEFAULT 'active',
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
    
    # Migration: Add 'status' column to licenses table if it doesn't exist
    try:
        c.execute("SELECT status FROM licenses LIMIT 1")
    except sqlite3.OperationalError:
        print("[WARNING]  Adding missing 'status' column to licenses table...")
        c.execute("ALTER TABLE licenses ADD COLUMN status TEXT DEFAULT 'active'")
        c.execute("UPDATE licenses SET status = CASE WHEN is_active = 1 THEN 'active' ELSE 'inactive' END")
        print("[OK] Migration completed: 'status' column added")
    
    conn.commit()
    conn.close()
    print("[OK] Database initialized")

# Auto-initialize database on startup (for Gunicorn/production)
try:
    init_db()
    print("[STARTUP] [SUCCESS] Database auto-initialized")
except Exception as e:
    print(f"[STARTUP] [WARNING]  Database init error (will retry): {e}")

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


@app.route('/guide')
def guide():
    """Trang hướng dẫn sử dụng"""
    return render_template('guide.html')


@app.route('/payment/success')
def payment_success_page():
    """Trang hiển thị license key sau khi thanh toán thành công"""
    return render_template('payment_success.html')


@app.route('/api/payment/check-order', methods=['GET'])
def check_order():
    """
    Kiểm tra thông tin đơn hàng và license key
    GET: /api/payment/check-order?order_id=123456
    
    Returns:
        {
            "success": true/false,
            "order_id": "123456",
            "email": "user@example.com",
            "plan_type": "lifetime",
            "payment_status": "completed/pending",
            "license_key": "xxx-xxx-xxx" (nếu đã thanh toán)
        }
    """
    try:
        order_id = request.args.get('order_id', '').strip()
        
        print(f"\n[CHECK-ORDER] 🔍 Request for order_id: {order_id}")
        print(f"[CHECK-ORDER] 📂 Database path: {DATABASE}")
        print(f"[CHECK-ORDER] 📂 Database exists: {os.path.exists(DATABASE)}")
        
        if not order_id:
            print(f"[CHECK-ORDER] [ERROR] Missing order_id")
            return jsonify({
                'success': False,
                'error': 'Missing order_id parameter'
            }), 400
        
        # Query database
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
        except Exception as db_error:
            print(f"[CHECK-ORDER] [ERROR] Database connection error: {db_error}")
            return jsonify({
                'success': False,
                'error': f'Database error: {str(db_error)}'
            }), 500
        
        try:
            c.execute('''
                SELECT o.order_id, o.customer_email, o.plan_type, o.payment_status, 
                       l.license_key, l.expiry_date, l.status
                FROM orders o
                LEFT JOIN licenses l ON o.order_id = l.order_id
                WHERE o.order_id = ?
            ''', (str(order_id),))
            
            result = c.fetchone()
        except Exception as sql_error:
            conn.close()
            print(f"[CHECK-ORDER] [ERROR] SQL query error: {sql_error}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'SQL error: {str(sql_error)}'
            }), 500
        
        conn.close()
        
        if not result:
            print(f"[CHECK-ORDER] [ERROR] Order not found: {order_id}")
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        order_id, email, plan_type, payment_status, license_key, expiry_date, license_status = result
        
        print(f"[CHECK-ORDER] 📦 Found order: payment_status={payment_status}, has_license={bool(license_key)}")
        
        # Check if payment completed and license generated
        if payment_status == 'completed' and license_key:
            print(f"[CHECK-ORDER] [SUCCESS] Returning completed order with license")
            return jsonify({
                'success': True,
                'order_id': order_id,
                'email': email,
                'plan_type': plan_type,
                'payment_status': payment_status,
                'license_key': license_key,
                'expiry_date': expiry_date,
                'license_status': license_status
            }), 200
        else:
            error_msg = 'Payment not completed yet' if payment_status == 'pending' else 'License not generated'
            print(f"[CHECK-ORDER] ⏳ Order not ready: {error_msg}")
            return jsonify({
                'success': False,
                'order_id': order_id,
                'email': email,
                'plan_type': plan_type,
                'payment_status': payment_status,
                'error': error_msg
            }), 200
            
    except Exception as e:
        print(f"[ERROR] Error checking order: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
            # Kích hoạt lần đầu - lưu theo múi giờ +7 (Việt Nam)
            activation_date = get_vietnam_isoformat()
            
            # Tính expiry date dựa vào plan - theo múi giờ +7 (Việt Nam)
            if plan_type == 'lifetime':
                expiry_date = None
            elif plan_type == 'yearly':
                expiry_date = (get_vietnam_time() + datetime.timedelta(days=365)).isoformat()
            elif plan_type == 'monthly':
                expiry_date = (get_vietnam_time() + datetime.timedelta(days=30)).isoformat()
            
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

@app.route('/api/protection/verify', methods=['POST'])
def verify_protection():
    """
    Xác thực hệ thống bảo vệ
    POST: {
        "hardware_id": "unique-hardware-id",
        "timestamp": 1234567890,
        "signature": "hmac-signature",
        "app_name": "VietnameseOCRTool"
    }
    """
    try:
        data = request.get_json()
        hardware_id = data.get('hardware_id', '').strip()
        timestamp = data.get('timestamp', 0)
        signature = data.get('signature', '').strip()
        app_name = data.get('app_name', '').strip()
        
        if not all([hardware_id, signature, app_name]):
            return jsonify({
                'valid': False,
                'error': 'Missing required fields'
            }), 400
        
        # Kiểm tra timestamp (không quá 5 phút)
        current_time = int(time.time())
        if abs(current_time - timestamp) > 300:
            return jsonify({
                'valid': False,
                'error': 'Request expired'
            }), 400
        
        # Tạo server signature để verify
        server_message = f"{hardware_id}-{timestamp}"
        server_signature = hmac.new(
            b'vietnamese_ocr_protection_key_2024',
            server_message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify signature
        if not hmac.compare_digest(signature, server_signature):
            return jsonify({
                'valid': False,
                'error': 'Invalid signature'
            }), 400
        
        # Tạo session token
        session_token = secrets.token_urlsafe(32)
        
        # Lưu session vào database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Tạo bảng sessions nếu chưa có
        c.execute('''
            CREATE TABLE IF NOT EXISTS protection_sessions (
                session_token TEXT PRIMARY KEY,
                hardware_id TEXT,
                app_name TEXT,
                created_at TEXT,
                last_activity TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Lưu session
        now = datetime.datetime.now().isoformat()
        c.execute('''
            INSERT OR REPLACE INTO protection_sessions 
            (session_token, hardware_id, app_name, created_at, last_activity, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (session_token, hardware_id, app_name, now, now))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'valid': True,
            'session_token': session_token,
            'expires_in': 3600  # 1 giờ
        }), 200
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Protection verification error: {str(e)}'
        }), 500

@app.route('/api/protection/check', methods=['POST'])
def check_protection_session():
    """
    Kiểm tra session bảo vệ
    POST: {
        "session_token": "session-token",
        "hardware_id": "hardware-id"
    }
    """
    try:
        data = request.get_json()
        session_token = data.get('session_token', '').strip()
        hardware_id = data.get('hardware_id', '').strip()
        
        if not session_token or not hardware_id:
            return jsonify({
                'valid': False,
                'error': 'Missing session_token or hardware_id'
            }), 400
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Kiểm tra session
        c.execute('''
            SELECT hardware_id, created_at, last_activity, is_active
            FROM protection_sessions 
            WHERE session_token = ? AND is_active = 1
        ''', (session_token,))
        
        result = c.fetchone()
        
        if not result:
            conn.close()
            return jsonify({
                'valid': False,
                'error': 'Invalid or expired session'
            }), 200
        
        db_hardware_id, created_at, last_activity, is_active = result
        
        # Kiểm tra hardware ID
        if db_hardware_id != hardware_id:
            conn.close()
            return jsonify({
                'valid': False,
                'error': 'Hardware ID mismatch'
            }), 200
        
        # Kiểm tra session timeout (1 giờ)
        created_dt = datetime.datetime.fromisoformat(created_at)
        if datetime.datetime.now() - created_dt > datetime.timedelta(hours=1):
            # Deactivate session
            c.execute('''
                UPDATE protection_sessions 
                SET is_active = 0 
                WHERE session_token = ?
            ''', (session_token,))
            conn.commit()
            conn.close()
            
            return jsonify({
                'valid': False,
                'error': 'Session expired'
            }), 200
        
        # Update last activity
        now = datetime.datetime.now().isoformat()
        c.execute('''
            UPDATE protection_sessions 
            SET last_activity = ? 
            WHERE session_token = ?
        ''', (now, session_token))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'valid': True,
            'message': 'Session is valid'
        }), 200
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Session check error: {str(e)}'
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
        created_at = get_vietnam_isoformat()
        
        # Tính expiry date cho preview - theo múi giờ +7 (Việt Nam)
        if plan_type == 'lifetime':
            expiry_date = None
        elif plan_type == 'yearly':
            expiry_date = (get_vietnam_time() + datetime.timedelta(days=365)).isoformat()
        elif plan_type == 'monthly':
            expiry_date = (get_vietnam_time() + datetime.timedelta(days=30)).isoformat()
        
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
        
        # 🔥 GỬI EMAIL CHO KHÁCH HÀNG (nếu có email)
        email_sent = False
        email_result = None
        
        if EMAIL_ENABLED and email:
            try:
                # Gửi email cho mỗi license key đã tạo
                for license_key in created_keys:
                    result = send_license_email(
                        to_email=email,
                        license_key=license_key,
                        customer_name=email.split('@')[0],  # Lấy tên từ email
                        order_id='ADMIN-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
                        plan_type=plan_type
                    )
                    
                    if result['success']:
                        email_sent = True
                        email_result = f"Sent via {result['account_used']}"
                        print(f"[SUCCESS] Email sent to {email} via {result['account_used']}")
                        print(f"   License: {license_key}")
                    else:
                        print(f"[ERROR] Failed to send email: {result['message']}")
                        email_result = f"Failed: {result['message']}"
            except Exception as e:
                print(f"[ERROR] Email error: {e}")
                email_result = f"Error: {str(e)}"
        
        response = {
            'success': True,
            'licenses': created_keys,
            'plan': plan_type,
            'quantity': quantity
        }
        
        # Thêm thông tin email vào response
        if email:
            response['email'] = email
            response['email_sent'] = email_sent
            if email_result:
                response['email_result'] = email_result
        
        return jsonify(response), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check_license', methods=['POST'])
def check_license():
    """
    Kiểm tra license key
    POST: {
        "license_key": "LICENSE-KEY",
        "hardware_id": "hardware-id",
        "app_name": "VietnameseOCRTool"
    }
    """
    try:
        data = request.get_json()
        license_key = data.get('license_key', '').strip()
        hardware_id = data.get('hardware_id', '').strip()
        app_name = data.get('app_name', '').strip()
        
        if not all([license_key, hardware_id, app_name]):
            return jsonify({
                'valid': False,
                'error': 'Missing required fields'
            }), 400
        
        # Kiểm tra license trong database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, license_key, machine_id, status, plan_type, created_at, expiry_date
            FROM licenses 
            WHERE license_key = ? AND status = 'active'
        ''', (license_key,))
        
        license_data = c.fetchone()
        
        if not license_data:
            conn.close()
            return jsonify({
                'valid': False,
                'error': 'Invalid license key'
            }), 400
        
        # Kiểm tra hardware binding
        if license_data[2] and license_data[2] != hardware_id:
            conn.close()
            return jsonify({
                'valid': False,
                'error': 'License bound to different hardware'
            }), 400
        
        # Kiểm tra expiration
        if license_data[6]:  # expiry_date
            from datetime import datetime
            expires_at = datetime.fromisoformat(license_data[6])
            if datetime.now() > expires_at:
                conn.close()
                return jsonify({
                    'valid': False,
                    'error': 'License expired'
                }), 400
        
        conn.close()
        
        return jsonify({
            'valid': True,
            'license_id': license_data[0],
            'plan': license_data[4],
            'created_at': license_data[5],
            'expires_at': license_data[6]
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Server error: {str(e)}'
        }), 500

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


# ==============================================================================
# DEBUG ENDPOINT - EMAIL CONFIG
# ==============================================================================

@app.route('/api/debug/email-config', methods=['GET'])
def debug_email_config():
    """
    🔍 Debug endpoint - Kiểm tra email configuration
    Endpoint công khai để debug (KHÔNG yêu cầu auth)
    
    Truy cập: https://ocr-uufr.onrender.com/api/debug/email-config
    """
    import os
    import json
    
    result = {
        'timestamp': datetime.datetime.now().isoformat(),
        'env_var_exists': False,
        'env_var_length': 0,
        'parse_success': False,
        'accounts_count': 0,
        'accounts': [],
        'error': None,
        'status': 'UNKNOWN'
    }
    
    # Kiểm tra biến môi trường
    email_accounts_env = os.getenv('EMAIL_ACCOUNTS')
    
    if not email_accounts_env:
        result['error'] = 'EMAIL_ACCOUNTS environment variable not found'
        result['status'] = 'ERROR - Env var missing'
        result['fix'] = 'Add EMAIL_ACCOUNTS to Render Environment Variables'
        return jsonify(result), 200
    
    result['env_var_exists'] = True
    result['env_var_length'] = len(email_accounts_env)
    result['first_50_chars'] = email_accounts_env[:50] + '...'
    
    # Thử parse JSON
    try:
        accounts = json.loads(email_accounts_env)
        result['parse_success'] = True
        result['accounts_count'] = len(accounts)
        
        # Hiển thị thông tin accounts (che password)
        for acc in accounts:
            result['accounts'].append({
                'email': acc.get('email', 'MISSING'),
                'has_password': bool(acc.get('password')),
                'password_length': len(acc.get('password', '')),
                'daily_limit': acc.get('daily_limit', 'MISSING')
            })
        
        result['status'] = 'OK - Email config will work!'
        result['message'] = f'[SUCCESS] Found {len(accounts)} email account(s)'
        
    except json.JSONDecodeError as e:
        result['error'] = f'JSON Parse Error: {str(e)}'
        result['status'] = 'ERROR - Invalid JSON format'
        result['fix'] = 'Check EMAIL_ACCOUNTS format: must use double quotes " not single quotes \''
    
    return jsonify(result), 200


@app.route('/api/debug/test-email', methods=['POST'])
def debug_test_email():
    """
    🧪 Test gửi email thật
    POST: {"to_email": "test@example.com"}
    """
    try:
        data = request.get_json() or {}
        to_email = data.get('to_email', 'hoangtuan.th484@gmail.com')
        
        if not EMAIL_ENABLED:
            return jsonify({
                'success': False,
                'error': 'EMAIL_ENABLED = False',
                'fix': 'Check email_sender.py import'
            }), 500
        
        # Thử gửi email test
        result = send_license_email(
            to_email=to_email,
            license_key='TEST-1234-5678-ABCD',
            customer_name='Test User',
            order_id='TEST-ORDER-001',
            plan_type='lifetime'
        )
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'account_used': result.get('account_used', 'none'),
            'to_email': to_email
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/debug/payos-config', methods=['GET'])
def debug_payos_config():
    """
    🔍 Kiểm tra PayOS configuration
    GET: /api/debug/payos-config
    """
    try:
        return jsonify({
            'payos_enabled': PAYOS_ENABLED,
            'client_id': PAYOS_CLIENT_ID if PAYOS_CLIENT_ID else 'NOT_SET',
            'api_key_masked': (PAYOS_API_KEY[:8] + '...' + PAYOS_API_KEY[-4:]) if PAYOS_API_KEY else 'NOT_SET',
            'checksum_masked': (PAYOS_CHECKSUM_KEY[:8] + '...' + PAYOS_CHECKSUM_KEY[-4:]) if PAYOS_CHECKSUM_KEY else 'NOT_SET',
            'config_status': 'OK' if (PAYOS_CLIENT_ID and PAYOS_API_KEY and PAYOS_CHECKSUM_KEY) else 'MISSING_CREDENTIALS',
            'instructions': {
                'step1': 'Add environment variables in Render Dashboard',
                'step2': 'PAYOS_CLIENT_ID = 4bbbd884-88f2-410c-9dc8-6782980ef64f',
                'step3': 'PAYOS_API_KEY = dd9f4ba8-cc6b-46e8-9afb-930972bf7531',
                'step4': 'PAYOS_CHECKSUM_KEY = a1e68d7351f461fa646a0fbd8f20563bcfb8080c44d50eb54df2f9ed9a0bfd7d'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'payos_enabled': False
        }), 500


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


def auto_generate_license(order_id, plan_type, customer_email, transaction_ref):
    """
    Tự động tạo license key (dùng cho PayOS webhook)
    Returns: license_key or None
    """
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Check if license already generated for this order
        c.execute('SELECT license_key FROM orders WHERE order_id = ? AND license_key IS NOT NULL', (str(order_id),))
        existing = c.fetchone()
        
        if existing:
            print(f"[WARNING] License already exists for order {order_id}")
            conn.close()
            return existing[0]
        
        # Generate new license
        license_key = generate_license_key()
        created_at = get_vietnam_isoformat()
        
        # Calculate expiry date - theo múi giờ +7 (Việt Nam)
        if plan_type == 'lifetime':
            expiry_date = None
        elif plan_type == 'yearly':
            expiry_date = (get_vietnam_time() + datetime.timedelta(days=365)).isoformat()
        elif plan_type == 'monthly':
            expiry_date = (get_vietnam_time() + datetime.timedelta(days=30)).isoformat()
        else:
            expiry_date = None
        
        # Insert license
        c.execute('''
            INSERT INTO licenses 
            (license_key, email, plan_type, created_at, is_active, order_id)
            VALUES (?, ?, ?, ?, 1, ?)
        ''', (license_key, customer_email, plan_type, created_at, str(order_id)))
        
        # Update order status
        c.execute('''
            UPDATE orders 
            SET payment_status = 'completed',
                transaction_id = ?,
                license_key = ?,
                paid_at = ?,
                expires_at = ?
            WHERE order_id = ?
        ''', (transaction_ref, license_key, created_at, expiry_date, str(order_id)))
        
        conn.commit()
        conn.close()
        
        print(f"[SUCCESS] Auto-generated license: {license_key}")
        print(f"   Order ID: {order_id}")
        print(f"   Email: {customer_email}")
        
        # 🔥 GỬI EMAIL CHO KHÁCH HÀNG
        if EMAIL_ENABLED and customer_email:
            try:
                result = send_license_email(
                    to_email=customer_email,
                    license_key=license_key,
                    customer_name=customer_email.split('@')[0],
                    order_id=str(order_id),
                    plan_type=plan_type
                )
                
                if result['success']:
                    print(f"[SUCCESS] Email sent to {customer_email} via {result['account_used']}")
                else:
                    print(f"[ERROR] Failed to send email: {result['message']}")
            except Exception as e:
                print(f"[ERROR] Email error: {e}")
        
        return license_key
        
    except Exception as e:
        print(f"[ERROR] Error generating license: {e}")
        import traceback
        traceback.print_exc()
        return None


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
        created_at = get_vietnam_isoformat()
        
        # Calculate expiry date based on plan - theo múi giờ +7 (Việt Nam)
        plan_info = get_plan_info(plan_type)
        if plan_info['duration_days'] >= 36500:  # Lifetime
            expiry_date = None
        else:
            expiry = get_vietnam_time() + datetime.timedelta(days=plan_info['duration_days'])
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
        
        print(f"[SUCCESS] Auto-generated license: {license_key} for order: {order_id}")
        
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
                    print(f"[SUCCESS] Email sent to {customer_email} via {result['account_used']}")
                else:
                    print(f"[ERROR] Failed to send email: {result['message']}")
            except Exception as e:
                print(f"[ERROR] Email error: {e}")
        
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

@app.route('/api/debug/payos-status', methods=['GET'])
def debug_payos_status():
    """Debug endpoint to check PayOS configuration"""
    return jsonify({
        'payos_enabled': PAYOS_ENABLED,
        'has_client_id': bool(os.getenv('PAYOS_CLIENT_ID')),
        'has_api_key': bool(os.getenv('PAYOS_API_KEY')),
        'has_checksum_key': bool(os.getenv('PAYOS_CHECKSUM_KEY')),
        'client_id_preview': os.getenv('PAYOS_CLIENT_ID', '')[:8] + '...' if os.getenv('PAYOS_CLIENT_ID') else 'NOT_SET'
    }), 200


@app.route('/api/debug/test-payment', methods=['POST'])
def debug_test_payment():
    """Test PayOS payment creation with detailed error logging"""
    try:
        data = request.get_json() or {}
        test_email = data.get('email', 'test@example.com')
        test_amount = int(data.get('amount', 10000))  # 10k VND để test
        
        # Check PayOS enabled
        if not PAYOS_ENABLED:
            return jsonify({
                'error': 'PayOS not enabled',
                'details': 'Check environment variables'
            }), 503
        
        # Try to create payment
        from payos_handler import create_payment_link
        
        test_order_id = int(datetime.datetime.now().timestamp() * 1000)
        
        result = create_payment_link(
            order_id=test_order_id,
            amount=test_amount,
            description=f"TEST - {test_email}",
            customer_email=test_email,
            return_url="https://ocr-uufr.onrender.com/success",
            cancel_url="https://ocr-uufr.onrender.com/failed"
        )
        
        return jsonify({
            'test_order_id': test_order_id,
            'payos_result': result
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/payment/create-order', methods=['POST'])
def create_payment_order():
    """
    Tạo đơn hàng mới - CHỈ DÙNG PAYOS (không dùng VietQR manual)
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
        
        # Kiểm tra PayOS có được kích hoạt không
        if not PAYOS_ENABLED:
            return jsonify({
                'error': 'PayOS not configured',
                'message': 'Payment system is not available. Please contact administrator.'
            }), 503
        
        # Tạo order ID (số nguyên cho PayOS) - theo múi giờ +7 (Việt Nam)
        order_id = int(get_vietnam_time().timestamp() * 1000)
        created_at = get_vietnam_isoformat()
        
        # Lưu order vào database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO orders 
            (order_id, plan_type, amount, customer_email, payment_method, payment_status, created_at)
            VALUES (?, ?, ?, ?, 'payos', 'pending', ?)
        ''', (str(order_id), plan_type, amount, customer_email, created_at))
        
        conn.commit()
        conn.close()
        
        # 🔥 TẠO PAYOS PAYMENT LINK (CHỈ DÙNG PAYOS)
        try:
            payos_result = create_payment_link(
                order_id=order_id,
                amount=amount,
                description=f"Mua license OCR - {plan_type} - {customer_email}",
                customer_email=customer_email,
                return_url=f"https://ocr-uufr.onrender.com/payment/success?order_id={order_id}",
                cancel_url="https://ocr-uufr.onrender.com/?cancel=true"
            )
            
            if not payos_result.get('success'):
                error_msg = payos_result.get('error', 'Unknown error')
                print(f"[ERROR] PayOS failed: {error_msg}")
                return jsonify({
                    'error': 'Payment creation failed',
                    'message': error_msg
                }), 500
            
            print(f"[SUCCESS] PayOS Payment Link created: {payos_result.get('payment_link_id')}")
            
            # 🔥 DEBUG: Log chi tiết response data
            print("========== BACKEND RESPONSE DATA ==========")
            print(f"payos_result keys: {list(payos_result.keys())}")
            print(f"checkout_url: {payos_result.get('checkout_url')}")
            print(f"qr_code: {'Present' if payos_result.get('qr_code') else 'MISSING'}")
            if payos_result.get('qr_code'):
                qr_len = len(payos_result.get('qr_code', ''))
                print(f"qr_code length: {qr_len}")
                print(f"qr_code first 50 chars: {payos_result.get('qr_code', '')[:50]}")
            print(f"payment_link_id: {payos_result.get('payment_link_id')}")
            print("==========================================")
            
            # Chỉ trả về PayOS data (không có VietQR)
            response_data = {
                'success': True,
                'order_id': str(order_id),
                'amount': amount,
                'checkout_url': payos_result.get('checkout_url'),
                'qr_code': payos_result.get('qr_code'),
                'payment_link_id': payos_result.get('payment_link_id')
            }
            
            print(f"Sending to frontend: {list(response_data.keys())}")
            return jsonify(response_data), 200
            
        except Exception as payos_error:
            print(f"[ERROR] PayOS error: {payos_error}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': 'Payment system error',
                'message': str(payos_error)
            }), 500
        
    except Exception as e:
        print(f"[ERROR] Error in create_payment_order: {e}")
        import traceback
        traceback.print_exc()
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
        
        # Tạo order - theo múi giờ +7 (Việt Nam)
        order_id = int(get_vietnam_time().timestamp() * 1000)  # PayOS yêu cầu số nguyên
        created_at = get_vietnam_isoformat()
        
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
            print(f"[SUCCESS] Created PayOS payment link for {customer_email}")
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
        print(f"[ERROR] Error creating payment: {e}")
        return jsonify({'error': str(e)}), 500


# [WARNING] DEPRECATED: This webhook is replaced by /payos/webhook (in payos_handler.py)
# Keeping for backward compatibility only
@app.route('/api/webhook/payos', methods=['POST', 'GET', 'HEAD', 'OPTIONS'])
def payos_webhook_legacy():
    """
    [DEPRECATED] Legacy PayOS webhook - redirects to new handler
    
    Use /payos/webhook instead (handled by payos_handler.py Blueprint)
    """
    print("[WARNING] Warning: Using deprecated webhook /api/webhook/payos")
    print("   Please update webhook URL to: /payos/webhook")
    
    # Redirect to new webhook handler
    if request.method in ['GET', 'HEAD', 'OPTIONS']:
        return jsonify({
            'status': 'deprecated',
            'message': 'Please use /payos/webhook instead',
            'new_url': 'https://ocr-uufr.onrender.com/payos/webhook'
        }), 200
    
    # For POST, try to process with auto_generate_license
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'ok', 'message': 'Webhook ready'}), 200
        
        payment_data = data.get('data', {})
        order_code = payment_data.get('orderCode')
        
        if not order_code:
            return jsonify({'error': 'No order code'}), 400
        
        # Find order and generate license
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT order_id, customer_email, plan_type, payment_status FROM orders WHERE order_id = ?', (str(order_code),))
        order = c.fetchone()
        conn.close()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        order_id, customer_email, plan_type, payment_status = order
        
        if payment_status == 'completed':
            return jsonify({'success': True, 'message': 'Already processed'}), 200
        
        transaction_ref = payment_data.get('reference', '')
        license_key = auto_generate_license(order_id, plan_type, customer_email, transaction_ref)
        
        if license_key:
            return jsonify({'success': True, 'order_id': order_id, 'license_key': license_key}), 200
        else:
            return jsonify({'error': 'Failed to generate license'}), 500
            
    except Exception as e:
        print(f"[ERROR] Legacy webhook error: {e}")
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
    print("[ROCKET] Vietnamese OCR Tool - License Server")
    print("="*60)
    print(f"Server running on: http://127.0.0.1:5000")
    print(f"Admin API Key: {ADMIN_API_KEY}")
    print("\nIMPORTANT: Change ADMIN_API_KEY in production!")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

