from flask import jsonify, request
import stripe
import json
from config import Config
from endpoints.blueprint_registry import checkout_bp
import logging

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@checkout_bp.route('/create-checkout-session', methods=['POST', 'OPTIONS'])
def create_checkout_session():
    if request.method == 'OPTIONS':
        return jsonify({"message": "CORS preflight passed"}), 200

    try:
        data = request.get_json()
        logger.info(f"Received request data: {data}")

        # Validate minimum required fields
        if not data.get('amount'):
            logger.error("Missing amount in request")
            return jsonify({"error": "Amount is required"}), 400
            
        if not data.get('customer_email'):
            logger.error("Missing customer_email in request")
            return jsonify({"error": "Customer email is required"}), 400
        
        logger.info("Creating Stripe checkout session...")
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': data.get('currency', 'usd'),
                    'unit_amount': data.get('amount'),
                    'product_data': {
                        'name': 'Payment',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=Config.DEFAULT_SUCCESS_URL,
            cancel_url=Config.DEFAULT_CANCEL_URL,
            customer_email=data.get('customer_email')
        )
        
        logger.info(f"Checkout session created successfully: {checkout_session.id}")

        # Return response in the format frontend expects
        return jsonify({
            "url": checkout_session.url,  # This is what frontend expects
            "code": 200,
            "data": {
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
            }
        }), 200

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
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