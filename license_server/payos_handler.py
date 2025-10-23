"""
PayOS Payment Handler - Flask Blueprint (Production Ready)
Optimized version with better error handling and PayOS compatibility
"""

import os
import hashlib
import hmac
import sqlite3
import datetime
import traceback
import time
import random
from flask import Blueprint, request, jsonify
from collections import defaultdict
from threading import Lock

# ============================================================================
# PayOS Configuration
# ============================================================================
PAYOS_CLIENT_ID = os.getenv('PAYOS_CLIENT_ID', '')
PAYOS_API_KEY = os.getenv('PAYOS_API_KEY', '')
PAYOS_CHECKSUM_KEY = os.getenv('PAYOS_CHECKSUM_KEY', '')

payos_client = None

# ============================================================================
# Anti-Spam / Rate Limiting
# ============================================================================
# Track webhook requests per IP to prevent spam attacks
webhook_rate_limit = defaultdict(list)  # {ip: [timestamp1, timestamp2, ...]}
rate_limit_lock = Lock()

# Rate limit settings
MAX_REQUESTS_PER_MINUTE = 10  # Allow max 10 webhook requests per minute per IP
MAX_REQUESTS_PER_HOUR = 100   # Allow max 100 webhook requests per hour per IP
RATE_LIMIT_WINDOW = 60        # 1 minute window

def generate_unique_order_id():
    """
    Generate unique order ID for PayOS
    Format: timestamp (10 digits) + random (4 digits) = 14 digits
    PayOS requires integer order code
    """
    timestamp = int(time.time())  # 10 digits
    random_suffix = random.randint(1000, 9999)  # 4 digits
    order_id = int(f"{timestamp}{random_suffix}")
    print(f"[PayOS] Generated order ID: {order_id}")
    return order_id


def check_rate_limit(ip_address):
    """
    Check if IP address has exceeded rate limit (anti-spam)
    
    Args:
        ip_address: IP address of the request
    
    Returns:
        (bool, str): (is_allowed, error_message)
    """
    with rate_limit_lock:
        current_time = time.time()
        
        # Clean up old entries (older than 1 hour)
        webhook_rate_limit[ip_address] = [
            timestamp for timestamp in webhook_rate_limit[ip_address]
            if current_time - timestamp < 3600  # Keep last hour
        ]
        
        # Get recent requests
        recent_requests = webhook_rate_limit[ip_address]
        requests_last_minute = sum(1 for t in recent_requests if current_time - t < 60)
        requests_last_hour = len(recent_requests)
        
        # Check rate limits
        if requests_last_minute >= MAX_REQUESTS_PER_MINUTE:
            return False, f"Rate limit exceeded: {requests_last_minute} requests in last minute (max {MAX_REQUESTS_PER_MINUTE})"
        
        if requests_last_hour >= MAX_REQUESTS_PER_HOUR:
            return False, f"Rate limit exceeded: {requests_last_hour} requests in last hour (max {MAX_REQUESTS_PER_HOUR})"
        
        # Add current request
        webhook_rate_limit[ip_address].append(current_time)
        
        return True, ""


def verify_webhook_signature(webhook_data, signature):
    """
    Verify PayOS webhook signature to prevent spam/fake webhooks
    
    PayOS uses HMAC-SHA256 with CHECKSUM_KEY
    
    Args:
        webhook_data: Raw JSON string from webhook body
        signature: Signature from 'x-signature' or 'webhook-signature' header
    
    Returns:
        bool: True if signature is valid
    """
    if not signature or not PAYOS_CHECKSUM_KEY:
        print("[WEBHOOK-VERIFY] ⚠️ Missing signature or checksum key")
        return False
    
    try:
        # Calculate HMAC-SHA256
        calculated_signature = hmac.new(
            PAYOS_CHECKSUM_KEY.encode('utf-8'),
            webhook_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (constant-time comparison to prevent timing attacks)
        is_valid = hmac.compare_digest(calculated_signature, signature)
        
        print(f"[WEBHOOK-VERIFY] Signature valid: {is_valid}")
        if not is_valid:
            print(f"[WEBHOOK-VERIFY] Expected: {calculated_signature[:20]}...")
            print(f"[WEBHOOK-VERIFY] Received: {signature[:20]}...")
        
        return is_valid
    except Exception as e:
        print(f"[WEBHOOK-VERIFY] ❌ Verification error: {e}")
        return False

def init_payos():
    """Initialize PayOS client (v1.0.0)"""
    global payos_client
    
    if not PAYOS_CLIENT_ID or not PAYOS_API_KEY or not PAYOS_CHECKSUM_KEY:
        print("❌ PayOS credentials not configured!")
        print(f"   CLIENT_ID: {'✓' if PAYOS_CLIENT_ID else '✗'}")
        print(f"   API_KEY: {'✓' if PAYOS_API_KEY else '✗'}")
        print(f"   CHECKSUM_KEY: {'✓' if PAYOS_CHECKSUM_KEY else '✗'}")
        return False
    
    try:
        from payos import PayOS
        from payos.types import ItemData, CreatePaymentLinkRequest  # v1.0.0
        
        payos_client = PayOS(
            client_id=PAYOS_CLIENT_ID,
            api_key=PAYOS_API_KEY,
            checksum_key=PAYOS_CHECKSUM_KEY
        )
        print("✅ PayOS v1.0.0 initialized successfully!")
        print(f"   Client ID: {PAYOS_CLIENT_ID[:8]}...")
        return True
    except ImportError as ie:
        print(f"❌ PayOS import error: {ie}")
        print("   Run: pip install payos")
        return False
    except Exception as e:
        print(f"❌ Error initializing PayOS: {e}")
        traceback.print_exc()
        return False


def create_payment_link(order_id, amount, description, customer_email="", return_url="", cancel_url=""):
    """
    Create PayOS payment link
    
    Args:
        order_id: Order ID (must be integer)
        amount: Amount in VND (integer)
        description: Payment description
        customer_email: Customer email (optional)
        return_url: Success redirect URL
        cancel_url: Cancel redirect URL
    
    Returns:
        dict: {
            'success': bool,
            'checkout_url': str,
            'qr_code': str,
            'order_id': str,
            'amount': int,
            'payment_link_id': str,
            'error': str (if failed)
        }
    """
    
    if not payos_client:
        return {'success': False, 'error': 'PayOS not initialized'}
    
    try:
        # Ensure order_id is integer - if not provided or invalid, generate unique one
        try:
            order_code = int(order_id)
        except (ValueError, TypeError):
            print(f"[PayOS] Invalid order_id '{order_id}', generating new unique ID...")
            order_code = generate_unique_order_id()
        
        # ✅ ĐÚNG CÁCH: Sử dụng payment_requests.create() với dict data
        # KHÔNG cần import ItemData, CreatePaymentLinkRequest
        payment_data = {
            "orderCode": order_code,
            "amount": int(amount),
            "description": description[:25],  # PayOS v1.0.0 limit: max 25 characters
            "returnUrl": return_url or f"https://ocr-uufr.onrender.com/payment/success?order_id={order_code}",
            "cancelUrl": cancel_url or f"https://ocr-uufr.onrender.com/payment/cancel?order_id={order_code}"
        }
        
        print(f"[PayOS] Creating payment request: Order {order_code}, Amount {amount:,} VND")
        print(f"[PayOS] Description: {description[:25]}")
        
        # ✅ PayOS v1.0.0 API: payment_requests.create() (KHÔNG phải payment_links)
        print(f"[PayOS] Calling payment_requests.create()...")
        response = payos_client.payment_requests.create(payment_data)
        
        print(f"[PayOS] Response received: {type(response)}")
        print(f"[PayOS] Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
        
        if response:
            print(f"[PayOS] ✅ Payment request created successfully!")
            
            # Extract fields - try multiple attribute names and dict access
            payment_link_id = None
            checkout_url = None
            qr_code = None
            
            # Try as object attributes first
            for attr in ['paymentLinkId', 'payment_link_id', 'id', 'orderId', 'order_id']:
                if hasattr(response, attr):
                    payment_link_id = getattr(response, attr)
                    break
            
            for attr in ['checkoutUrl', 'checkout_url', 'paymentUrl', 'payment_url', 'url']:
                if hasattr(response, attr):
                    checkout_url = getattr(response, attr)
                    break
            
            for attr in ['qrCode', 'qr_code', 'qrCodeUrl', 'qr_code_url']:
                if hasattr(response, attr):
                    qr_code = getattr(response, attr)
                    break
            
            # Try as dict if response is dict-like
            if isinstance(response, dict):
                payment_link_id = payment_link_id or response.get('paymentLinkId') or response.get('payment_link_id') or response.get('id')
                checkout_url = checkout_url or response.get('checkoutUrl') or response.get('checkout_url') or response.get('paymentUrl')
                qr_code = qr_code or response.get('qrCode') or response.get('qr_code')
            
            # Try response.data if exists
            if hasattr(response, 'data') and isinstance(response.data, dict):
                data = response.data
                payment_link_id = payment_link_id or data.get('paymentLinkId') or data.get('id')
                checkout_url = checkout_url or data.get('checkoutUrl') or data.get('checkout_url')
                qr_code = qr_code or data.get('qrCode') or data.get('qr_code')
            
            # Default values
            payment_link_id = payment_link_id or str(order_code)
            checkout_url = checkout_url or ''
            qr_code = qr_code or ''
            
            # 🔥 DEBUG: Log chi tiết PayOS API response
            print("========== PAYOS API RESPONSE DEBUG ==========")
            print(f"Response type: {type(response)}")
            print(f"Response dir: {dir(response)}")
            if hasattr(response, '__dict__'):
                print(f"Response __dict__: {response.__dict__}")
            if hasattr(response, 'data'):
                print(f"Response.data type: {type(response.data)}")
                print(f"Response.data: {response.data}")
            if isinstance(response, dict):
                print(f"Response as dict: {response}")
            print("==============================================")
            
            print(f"[PayOS]    Payment ID: {payment_link_id}")
            print(f"[PayOS]    Checkout URL: {checkout_url[:80]}..." if len(checkout_url) > 80 else f"[PayOS]    Checkout URL: {checkout_url}")
            print(f"[PayOS]    QR Code: {'✅ Present' if qr_code else '❌ MISSING'} (length: {len(qr_code) if qr_code else 0})")
            
            if qr_code:
                print(f"[PayOS]    QR Code first 100 chars: {qr_code[:100]}")
            
            if not checkout_url:
                print(f"[PayOS] ⚠️ WARNING: No checkout URL in response!")
                print(f"[PayOS] Full response: {response}")
                return {'success': False, 'error': 'No checkout URL in PayOS response'}
            
            result = {
                'success': True,
                'checkout_url': checkout_url,
                'qr_code': qr_code or '',  # Empty string if None
                'order_id': str(order_id),
                'amount': int(amount),
                'payment_link_id': payment_link_id
            }
            
            print(f"[PayOS] Returning result keys: {list(result.keys())}")
            return result
        else:
            print(f"[PayOS] ❌ No response from PayOS!")
            return {'success': False, 'error': 'No response from PayOS'}
            
    except ValueError as e:
        error_msg = f"Invalid order_id format: {e}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {'success': False, 'error': error_msg}
    except AttributeError as e:
        error_msg = f"PayOS response attribute error: {e}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {'success': False, 'error': error_msg}
    except Exception as e:
        error_msg = f"Error creating payment link: {e}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {'success': False, 'error': error_msg}


# Initialize PayOS
PAYOS_ENABLED = init_payos()

# ============================================================================
# Flask Blueprint
# ============================================================================

app = Blueprint('payos', __name__)

# Database configuration - use persistent disk on Render, local file in dev
import os as _os
PERSISTENT_DIR = '/var/data'
if _os.path.exists(PERSISTENT_DIR) and _os.access(PERSISTENT_DIR, _os.W_OK):
    DATABASE = _os.path.join(PERSISTENT_DIR, 'licenses.db')
else:
    DATABASE = 'licenses.db'


@app.route('/webhook', methods=['POST', 'GET', 'HEAD', 'OPTIONS'])
def webhook():
    """
    PayOS Webhook Handler
    
    Handles webhook callbacks from PayOS payment gateway
    Supports GET (verification), POST (payment data), OPTIONS (CORS)
    """
    
    # Log all incoming requests
    print(f"\n{'='*80}")
    print(f"[WEBHOOK] Method: {request.method}")
    print(f"[WEBHOOK] From: {request.remote_addr}")
    print(f"[WEBHOOK] URL: {request.url}")
    print(f"[WEBHOOK] Headers: {dict(request.headers)}")
    
    # ========================================================================
    # 🛡️ ANTI-SPAM: Check rate limit for this IP
    # ========================================================================
    client_ip = request.remote_addr or request.headers.get('X-Forwarded-For', 'unknown').split(',')[0].strip()
    
    # Skip rate limit for GET/OPTIONS (verification requests)
    if request.method == 'POST':
        is_allowed, error_msg = check_rate_limit(client_ip)
        if not is_allowed:
            print(f"[WEBHOOK] 🚫 RATE LIMIT EXCEEDED for IP {client_ip}")
            print(f"[WEBHOOK] 🚫 {error_msg}")
            return jsonify({
                'code': '99',
                'desc': 'Rate limit exceeded',
                'success': False,
                'error': error_msg
            }), 429  # 429 Too Many Requests
    
    # ========================================================================
    # Handle GET - PayOS verification test
    # ========================================================================
    if request.method == 'GET':
        print("[WEBHOOK] ✅ GET verification request")
        response = {
            'code': '00',
            'desc': 'success',
            'success': True,
            'data': {
                'status': 'webhook_active',
                'service': 'payos',
                'version': '2.0',
                'timestamp': datetime.datetime.now().isoformat()
            }
        }
        return jsonify(response), 200
    
    # ========================================================================
    # Handle OPTIONS/HEAD - CORS preflight
    # ========================================================================
    if request.method in ['OPTIONS', 'HEAD']:
        print("[WEBHOOK] ✅ CORS preflight request")
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, x-signature, webhook-id'
        return response, 200
    
    # ========================================================================
    # Handle POST - Actual webhook data
    # ========================================================================
    if request.method == 'POST':
        try:
            # Get raw body for debugging
            raw_body = request.get_data(as_text=True)
            print(f"[WEBHOOK] Raw body ({len(raw_body)} bytes)")
            if len(raw_body) < 1000:
                print(f"[WEBHOOK] Body: {raw_body}")
            else:
                print(f"[WEBHOOK] Body (first 500): {raw_body[:500]}...")
            
            # ================================================================
            # 🔒 SECURITY: Verify webhook signature to prevent spam/fake requests
            # ================================================================
            signature = request.headers.get('x-signature') or request.headers.get('webhook-signature') or request.headers.get('Webhook-Signature')
            
            if signature:
                print(f"[WEBHOOK] 🔐 Verifying signature: {signature[:20]}...")
                if not verify_webhook_signature(raw_body, signature):
                    print("[WEBHOOK] ❌ INVALID SIGNATURE - Rejecting webhook (possible spam/hack attempt)")
                    return jsonify({
                        'code': '99',
                        'desc': 'Invalid signature',
                        'success': False,
                        'error': 'Webhook signature verification failed'
                    }), 403  # 403 Forbidden
            else:
                # ⚠️ WARNING: No signature provided
                # In production, you should REJECT requests without signature
                # For now, we log a warning but allow it (for backward compatibility)
                print("[WEBHOOK] ⚠️ WARNING: No signature header found!")
                print("[WEBHOOK] ⚠️ This webhook is vulnerable to spam attacks!")
                print("[WEBHOOK] ⚠️ Expected header: 'x-signature' or 'webhook-signature'")
                # TODO: Uncomment this in production after PayOS confirms signature header name
                # return jsonify({
                #     'code': '99',
                #     'desc': 'Missing signature',
                #     'success': False,
                #     'error': 'Webhook signature required'
                # }), 401  # 401 Unauthorized
            
            # Parse JSON (force=True to handle incorrect Content-Type)
            try:
                data = request.get_json(force=True)
            except Exception as parse_error:
                print(f"[WEBHOOK] ❌ JSON parse error: {parse_error}")
                return jsonify({
                    'code': '99',
                    'desc': 'Invalid JSON',
                    'success': False
                }), 400
            
            # Empty payload = test ping
            if not data:
                print("[WEBHOOK] ⚠️ Empty payload (test ping)")
                return jsonify({
                    'code': '00',
                    'desc': 'success',
                    'success': True,
                    'message': 'Webhook ready'
                }), 200
            
            print(f"[WEBHOOK] 📦 Parsed data: {data}")
            
            # ================================================================
            # Extract payment information (handle multiple formats)
            # ================================================================
            
            # Format 1: Standard PayOS webhook format
            # { "code": "00", "desc": "success", "data": {...}, "success": true }
            code = data.get('code')
            desc = data.get('desc', '')
            success = data.get('success', False)
            payment_data = data.get('data', {})
            
            # Format 2: Direct payment data (no wrapper)
            # { "orderCode": 123, "amount": 10000, ... }
            if not code and not payment_data:
                # Treat entire data as payment_data
                if 'orderCode' in data:
                    print("[WEBHOOK] 📋 Direct payment data format (no wrapper)")
                    payment_data = data
                    code = '00'
                    success = True
            
            # Format 3: PayOS might send nested data
            if not payment_data and isinstance(data.get('data'), dict):
                payment_data = data.get('data', {})
            
            print(f"[WEBHOOK] Extracted: code={code}, success={success}")
            print(f"[WEBHOOK] Payment data: {payment_data}")
            
            # ================================================================
            # Validate payment status
            # ================================================================
            
            # Test ping (code='00' but no actual payment data)
            if code == '00' and success and not payment_data.get('orderCode'):
                print("[WEBHOOK] ✅ PayOS test ping successful")
                return jsonify({
                    'code': '00',
                    'desc': 'success',
                    'success': True
                }), 200
            
            # Payment failed
            if code != '00' or not success:
                print(f"[WEBHOOK] ❌ Payment failed: code={code}, desc={desc}")
                return jsonify({
                    'code': code or '99',
                    'desc': desc or 'Payment not successful',
                    'success': False
                }), 200  # Return 200 to prevent PayOS retry
            
            # ================================================================
            # Extract order details
            # ================================================================
            
            order_code = payment_data.get('orderCode')
            amount = payment_data.get('amount', 0)
            reference = payment_data.get('reference') or payment_data.get('transactionDateTime') or ''
            description = payment_data.get('description', '')
            
            # Validate order_code
            if not order_code:
                print("[WEBHOOK] ❌ Missing orderCode in payment data")
                print(f"[WEBHOOK] Available keys: {list(payment_data.keys())}")
                return jsonify({
                    'code': '99',
                    'desc': 'Missing orderCode',
                    'success': False
                }), 200
            
            print(f"[WEBHOOK] 💰 Payment details:")
            print(f"           Order Code: {order_code}")
            print(f"           Amount: {amount:,} VND")
            print(f"           Reference: {reference}")
            print(f"           Description: {description}")
            
            # ================================================================
            # Query database for order
            # ================================================================
            
            try:
                conn = sqlite3.connect(DATABASE)
                c = conn.cursor()
                
                c.execute('''
                    SELECT order_id, customer_email, plan_type, payment_status 
                    FROM orders 
                    WHERE order_id = ?
                ''', (str(order_code),))
                
                order = c.fetchone()
                
                if not order:
                    print(f"[WEBHOOK] ❌ Order not found: {order_code}")
                    conn.close()
                    return jsonify({
                        'code': '99',
                        'desc': 'Order not found in database',
                        'success': False
                    }), 200
                
                order_id, customer_email, plan_type, payment_status = order
                
                print(f"[WEBHOOK] 📋 Order found:")
                print(f"           Order ID: {order_id}")
                print(f"           Email: {customer_email}")
                print(f"           Plan: {plan_type}")
                print(f"           Status: {payment_status}")
                
                # Check if already processed
                if payment_status == 'completed':
                    print(f"[WEBHOOK] ℹ️ Order already processed: {order_id}")
                    conn.close()
                    return jsonify({
                        'code': '00',
                        'desc': 'Already processed',
                        'success': True,
                        'message': 'Order already completed'
                    }), 200
                
                conn.close()
                
            except sqlite3.Error as db_error:
                print(f"[WEBHOOK] ❌ Database error: {db_error}")
                return jsonify({
                    'code': '99',
                    'desc': 'Database error',
                    'success': False
                }), 500
            
            # ================================================================
            # Generate license key
            # ================================================================
            
            print(f"[WEBHOOK] 🔑 Generating license for order {order_id}...")
            
            try:
                # Try to import auto_generate_license from main app
                import sys
                if 'app' not in sys.modules:
                    print("[WEBHOOK] ⚠️ Main app module not loaded, attempting import...")
                    import app as main_app
                
                from app import auto_generate_license
                
                license_key = auto_generate_license(
                    order_id=order_id,
                    plan_type=plan_type,
                    customer_email=customer_email,
                    transaction_ref=reference
                )
                
                if license_key:
                    print(f"[WEBHOOK] ✅ SUCCESS!")
                    print(f"           License: {license_key}")
                    print(f"           Email: {customer_email}")
                    print(f"           Plan: {plan_type}")
                    print("="*80 + "\n")
                    
                    return jsonify({
                        'code': '00',
                        'desc': 'success',
                        'success': True,
                        'data': {
                            'order_id': order_id,
                            'license_key': license_key,
                            'email': customer_email
                        }
                    }), 200
                else:
                    print(f"[WEBHOOK] ❌ Failed to generate license (returned None)")
                    return jsonify({
                        'code': '99',
                        'desc': 'Failed to generate license',
                        'success': False
                    }), 500
                    
            except ImportError as import_error:
                print(f"[WEBHOOK] ❌ Import error: {import_error}")
                traceback.print_exc()
                return jsonify({
                    'code': '99',
                    'desc': 'Server configuration error',
                    'success': False
                }), 500
            
        except Exception as e:
            print(f"[WEBHOOK] ❌ EXCEPTION: {e}")
            traceback.print_exc()
            print("="*80 + "\n")
            return jsonify({
                'code': '99',
                'desc': str(e),
                'success': False
            }), 500
    
    # Unknown method
    print(f"[WEBHOOK] ❌ Method not allowed: {request.method}")
    return jsonify({
        'code': '99',
        'desc': 'Method not allowed',
        'success': False
    }), 405


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'PayOS Handler',
        'version': '2.0',
        'timestamp': datetime.datetime.now().isoformat(),
        'payos_enabled': PAYOS_ENABLED,
        'database': DATABASE,
        'endpoints': {
            'webhook': '/payos/webhook',
            'health': '/payos/health',
            'test': '/payos/test'
        }
    }), 200


@app.route('/test', methods=['GET'])
def test():
    """Test endpoint for webhook URL verification"""
    return jsonify({
        'status': 'ok',
        'message': 'PayOS webhook endpoint is working!',
        'service': 'payos',
        'timestamp': datetime.datetime.now().isoformat(),
        'webhook_url': 'https://ocr-uufr.onrender.com/payos/webhook',
        'methods_allowed': ['GET', 'POST', 'OPTIONS', 'HEAD']
    }), 200


@app.route('/simulate', methods=['POST'])
def simulate_payment():
    """
    Simulate a PayOS webhook for testing (REMOVE IN PRODUCTION!)
    
    Usage:
        POST /payos/simulate
        Body: {
            "orderCode": 123456,
            "amount": 2000,
            "description": "Test payment"
        }
    """
    try:
        test_data = request.get_json()
        order_code = test_data.get('orderCode', 123456)
        amount = test_data.get('amount', 2000)
        
        # Create fake PayOS webhook payload
        fake_webhook = {
            'code': '00',
            'desc': 'success',
            'success': True,
            'data': {
                'orderCode': order_code,
                'amount': amount,
                'description': test_data.get('description', 'Test payment'),
                'reference': f'TEST_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}',
                'transactionDateTime': datetime.datetime.now().isoformat()
            }
        }
        
        print(f"[SIMULATE] 🧪 Simulating webhook for order {order_code}")
        
        # Call webhook handler internally
        from flask import current_app
        with current_app.test_request_context(
            '/payos/webhook',
            method='POST',
            json=fake_webhook
        ):
            response = webhook()
            return response
        
    except Exception as e:
        print(f"[SIMULATE] ❌ Error: {e}")
        return jsonify({'error': str(e)}), 500