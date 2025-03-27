from flask import jsonify, request
import stripe
import json
from config import Config
from endpoints.init import checkout_bp

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

@checkout_bp.route('/create-checkout-session', methods=['POST', 'OPTIONS'])
def create_checkout_session():
    if request.method == 'OPTIONS':
        # Handle preflight request
        return jsonify({"message": "CORS preflight passed"}), 200

    """
    Create a new Stripe Checkout Session.
    
    Request body parameters:
    - amount: (required) Amount in cents
    - currency: (optional) 3-letter currency code, default 'usd'
    - metadata: (optional) Additional metadata (e.g., user_id)
    - success_url: (optional) URL to redirect on success
    - cancel_url: (optional) URL to redirect on cancel
    - customer_email: (optional) Pre-fill customer email
    
    Returns:
    - url: Checkout session URL
    """
    data = json.loads(request.data)
    try:
        # Validate minimum required fields
        if not data.get('amount'):
            return jsonify({"error": "Amount is required"}), 400
            
        # Always require customer email for logged in users
        if not data.get('customer_email'):
            return jsonify({"error": "Customer email is required"}), 400

        # Create a generic line item
        line_items = [{
            'price_data': {
                'currency': data.get('currency', 'usd'),
                'product_data': {
                    'name': data.get('product_name', 'Payment'),
                },
                'unit_amount': data.get('amount'),
            },
            'quantity': 1,
        }]
        
        # Add payment_method_options for 3D Secure
        session_params = {
            'payment_method_types': ['card'],
            'payment_method_options': {
                'card': {
                    'request_three_d_secure': 'any'  # Request 3DS when available
                }
            },
            'line_items': line_items,
            'mode': 'payment',
            'success_url': data.get('success_url', Config.DEFAULT_SUCCESS_URL),
            'cancel_url': data.get('cancel_url', Config.DEFAULT_CANCEL_URL),
            'customer_email': data.get('customer_email'),  # Use authenticated email
        }
        
        # Add optional parameters if provided
        if data.get('metadata'):
            session_params['metadata'] = data.get('metadata')
        
        # Create the Checkout Session
        checkout_session = stripe.checkout.Session.create(**session_params)
        
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Add endpoint to handle 3D Secure authentication completion
@checkout_bp.route('/payment-auth-complete', methods=['POST'])
def payment_auth_complete():
    try:
        intent = stripe.PaymentIntent.retrieve(request.json['payment_intent'])
        
        if intent.status == 'requires_action':
            return jsonify({
                'requires_action': True,
                'payment_intent_client_secret': intent.client_secret
            })
        elif intent.status == 'succeeded':
            return jsonify({
                'success': True
            })
        else:
            return jsonify({
                'error': 'Payment authentication failed'
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@checkout_bp.route('/checkout-session', methods=['GET'])
def get_checkout_session():
    """
    Retrieve details of a Checkout Session.
    
    Query parameters:
    - session_id: (required) Checkout Session ID
    
    Returns:
    - payment_intent: Associated Payment Intent ID
    - amount_total: Total amount in cents
    - currency: Currency code
    - customer_email: Customer email if available
    - payment_status: Payment status
    - metadata: Session metadata
    """
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({"error": "Session ID is required"}), 400
    
    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Extract relevant information
        response_data = {
            "payment_intent": session.payment_intent,
            "amount_total": session.amount_total,
            "currency": session.currency,
            "customer_email": session.customer_email,
            "payment_status": session.payment_status,
            "metadata": session.metadata
        }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400