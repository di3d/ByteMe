from flask import jsonify, request
import stripe
import json
from config import Config
from endpoints.init import payment_bp

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Removed synchronous payment intent functionality

@payment_bp.route('/payment-intent/<payment_intent_id>', methods=['GET'])
def get_payment_intent(payment_intent_id):
    """
    Retrieve details of a Payment Intent.
    
    Path parameters:
    - payment_intent_id: (required) Payment Intent ID
    
    Returns:
    - id: Payment Intent ID
    - amount: Amount in cents
    - currency: Currency code
    - status: Payment status
    - metadata: Payment metadata
    """
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        return jsonify({
            'id': payment_intent.id,
            'amount': payment_intent.amount,
            'currency': payment_intent.currency,
            'status': payment_intent.status,
            'metadata': payment_intent.metadata
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400