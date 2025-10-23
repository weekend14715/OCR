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
from flask import Blueprint, request, jsonify

# ============================================================================
# PayOS Configuration
# ============================================================================
PAYOS_CLIENT_ID = os.getenv('PAYOS_CLIENT_ID', '')
PAYOS_API_KEY = os.getenv('PAYOS_API_KEY', '')
PAYOS_CHECKSUM_KEY = os.getenv('PAYOS_CHECKSUM_KEY', '')

payos_client = None

def init_payos():
    """Initialize PayOS client"""
    global payos_client
    
    if not PAYOS_CLIENT_ID or not PAYOS_API_KEY or not PAYOS_CHECKSUM_KEY:
        print("❌ PayOS credentials not configured!")
        print(f"   CLIENT_ID: {'✓' if PAYOS_CLIENT_ID else '✗'}")
        print(f"   API_KEY: {'✓' if PAYOS_API_KEY else '✗'}")
        print(f"   CHECKSUM_KEY: {'✓' if PAYOS_CHECKSUM_KEY else '✗'}")
        return False
    
    try:
        from payos import PayOS
        payos_client = PayOS(
            client_id=PAYOS_CLIENT_ID,
            api_key=PAYOS_API_KEY,
            checksum_key=PAYOS_CHECKSUM_KEY
        )
        print("✅ PayOS initialized successfully!")
        print(f"   Client ID: {PAYOS_CLIENT_ID[:8]}...")
        return True
    except ImportError:
        print("❌ PayOS library not installed. Run: pip install payos")
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
        # Ensure order_id is integer
        order_code = int(order_id)
        
        payment_data = {
            "orderCode": order_code,
            "amount": int(amount),
            "description": description[:25],  # PayOS v1.0.0 limit: max 25 characters
            "returnUrl": return_url or "https://ocr-uufr.onrender.com/payment/success",
            "cancelUrl": cancel_url or "https://ocr-uufr.onrender.com/payment/cancel"
        }
        
        print(f"[PayOS] Creating payment link: Order {order_code}, Amount {amount:,} VND")
        
        # PayOS v1.0.0 new API
        response = payos_client.payment_requests.create(payment_data)
        
        if response:
            print(f"[PayOS] ✅ Payment link created successfully!")
            print(f"[PayOS]    Link ID: {response.paymentLinkId}")
            
            return {
                'success': True,
                'checkout_url': response.checkoutUrl,
                'qr_code': response.qrCode,
                'order_id': str(order_id),
                'amount': int(amount),
                'payment_link_id': response.paymentLinkId
            }
        else:
            return {'success': False, 'error': 'No response from PayOS'}
            
    except ValueError as e:
        print(f"❌ Invalid order_id format: {e}")
        return {'success': False, 'error': f'Invalid order_id: {e}'}
    except Exception as e:
        print(f"❌ Error creating payment link: {e}")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


# Initialize PayOS
PAYOS_ENABLED = init_payos()

# ============================================================================
# Flask Blueprint
# ============================================================================

app = Blueprint('payos', __name__)
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