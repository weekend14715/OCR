"""
PayOS Payment Handler - Flask Blueprint (Fixed Version)
"""

import os
import hashlib
import hmac
import sqlite3
import datetime
import traceback
from flask import Blueprint, request, jsonify

# Khởi tạo PayOS client
PAYOS_CLIENT_ID = os.getenv('PAYOS_CLIENT_ID', '')
PAYOS_API_KEY = os.getenv('PAYOS_API_KEY', '')
PAYOS_CHECKSUM_KEY = os.getenv('PAYOS_CHECKSUM_KEY', '')

payos_client = None

def init_payos():
    """Khởi tạo PayOS client"""
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
        return True
    except ImportError:
        print("❌ PayOS library not installed. Run: pip install payos")
        return False
    except Exception as e:
        print(f"❌ Error initializing PayOS: {e}")
        traceback.print_exc()
        return False


def create_payment_link(order_id, amount, description, customer_email="", return_url="", cancel_url=""):
    """Tạo link thanh toán PayOS"""
    
    if not payos_client:
        return {'success': False, 'error': 'PayOS not initialized'}
    
    try:
        payment_data = {
            "orderCode": int(order_id),
            "amount": int(amount),
            "description": description,
            "returnUrl": return_url or "https://your-app.com/payment/success",
            "cancelUrl": cancel_url or "https://your-app.com/payment/cancel"
        }
        
        response = payos_client.createPaymentLink(payment_data)
        
        if response:
            return {
                'success': True,
                'checkout_url': response.checkoutUrl,
                'qr_code': response.qrCode,
                'order_id': order_id,
                'amount': amount,
                'payment_link_id': response.paymentLinkId
            }
        else:
            return {'success': False, 'error': 'Failed to create payment link'}
            
    except Exception as e:
        print(f"❌ Error creating payment link: {e}")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


# Khởi tạo
PAYOS_ENABLED = init_payos()

# ==============================================================================
# FLASK BLUEPRINT
# ==============================================================================

app = Blueprint('payos', __name__)
DATABASE = 'licenses.db'


@app.route('/webhook', methods=['POST', 'GET', 'HEAD', 'OPTIONS'])
def webhook():
    """
    PayOS Webhook Handler - FIXED VERSION
    """
    
    # Log tất cả request
    print("\n" + "="*80)
    print(f"[WEBHOOK] Method: {request.method}")
    print(f"[WEBHOOK] URL: {request.url}")
    print(f"[WEBHOOK] Headers: {dict(request.headers)}")
    print(f"[WEBHOOK] Remote IP: {request.remote_addr}")
    
    # Handle preflight/OPTIONS
    if request.method in ['OPTIONS', 'HEAD']:
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, x-signature'
        print("[WEBHOOK] ✅ Responding to preflight request")
        return response, 200
    
    # Handle GET (webhook verification từ PayOS)
    if request.method == 'GET':
        print("[WEBHOOK] ✅ GET request received - webhook is accessible!")
        return jsonify({
            'status': 'webhook_ready',
            'service': 'payos',
            'version': '2.0',
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
    
    # Handle POST (actual webhook data)
    try:
        # Get raw body for debugging
        raw_body = request.get_data(as_text=True)
        print(f"[WEBHOOK] Raw body: {raw_body[:500]}...")  # First 500 chars
        
        # Parse JSON
        data = request.get_json(force=True)  # force=True để parse ngay cả khi Content-Type không đúng
        
        if not data:
            print("[WEBHOOK] ⚠️ Empty payload")
            return jsonify({'status': 'ok', 'message': 'Empty payload accepted'}), 200
        
        print(f"[WEBHOOK] 📦 Parsed data: {data}")
        
        # Extract payment info
        code = data.get('code')
        desc = data.get('desc', '')
        success = data.get('success', False)
        payment_data = data.get('data', {})
        
        print(f"[WEBHOOK] Payment status: code={code}, success={success}")
        
        # Check payment success
        if code != '00' or not success:
            print(f"[WEBHOOK] ❌ Payment failed: {desc}")
            return jsonify({'error': 'Payment not successful', 'code': code}), 400
        
        # Get order details
        order_code = payment_data.get('orderCode')
        amount = payment_data.get('amount', 0)
        reference = payment_data.get('reference', '')
        description = payment_data.get('description', '')
        
        print(f"[WEBHOOK] 💰 Payment details:")
        print(f"           Order: {order_code}")
        print(f"           Amount: {amount:,} VND")
        print(f"           Reference: {reference}")
        
        if not order_code:
            print("[WEBHOOK] ❌ Missing order code")
            return jsonify({'error': 'Missing order code'}), 400
        
        # Query database
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
            return jsonify({'error': 'Order not found'}), 404
        
        order_id, customer_email, plan_type, payment_status = order
        
        # Check if already processed
        if payment_status == 'completed':
            print(f"[WEBHOOK] ℹ️ Order already processed: {order_id}")
            conn.close()
            return jsonify({'success': True, 'message': 'Already processed'}), 200
        
        conn.close()
        
        # Generate license
        print(f"[WEBHOOK] 🔑 Generating license for order {order_id}...")
        
        # Import here to avoid circular import
        import sys
        if 'app' in sys.modules:
            from app import auto_generate_license
            license_key = auto_generate_license(order_id, plan_type, customer_email, reference)
        else:
            print("[WEBHOOK] ❌ Cannot import auto_generate_license")
            return jsonify({'error': 'Server configuration error'}), 500
        
        if license_key:
            print(f"[WEBHOOK] ✅ SUCCESS!")
            print(f"           License: {license_key}")
            print(f"           Email: {customer_email}")
            print("="*80 + "\n")
            
            return jsonify({
                'success': True,
                'order_id': order_id,
                'license_key': license_key
            }), 200
        else:
            print(f"[WEBHOOK] ❌ Failed to generate license")
            return jsonify({'error': 'Failed to generate license'}), 500
        
    except Exception as e:
        print(f"[WEBHOOK] ❌ EXCEPTION: {e}")
        traceback.print_exc()
        print("="*80 + "\n")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'PayOS Handler',
        'timestamp': datetime.datetime.now().isoformat(),
        'payos_enabled': PAYOS_ENABLED,
        'endpoints': ['/payos/webhook', '/payos/health']
    }), 200


@app.route('/test', methods=['GET'])
def test():
    """Test endpoint để verify webhook URL"""
    return jsonify({
        'status': 'ok',
        'message': 'PayOS webhook is working!',
        'timestamp': datetime.datetime.now().isoformat()
    }), 200