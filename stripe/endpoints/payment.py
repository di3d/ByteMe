from flask import jsonify, request
import stripe
import json
from config import Config
from endpoints.init import payment_bp

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

@payment_bp.route('/payment-intent', methods=['POST'])
def create_payment_intent():
    """
    Create a new Payment Intent.
    
    Request body parameters:
    - amount: (required) Amount in cents
    - currency: (optional) 3-letter currency code, default 'usd'
    - payment_method_types: (optional) Array of payment methods, default ['card']
    - receipt_email: (optional) Email for receipt
    - metadata: (optional) Additional metadata
    - description: (optional) Payment description
    
    Returns:
    - success: True if successful
    - clientSecret: Client secret for the frontend
    - paymentIntentId: ID of the created Payment Intent
    """
    data = json.loads(request.data)
    try:
        if not data.get('amount'):
            return jsonify({"error": "Amount is required"}), 400
            
        # Create payment intent parameters
        payment_params = {
            'amount': data.get('amount'),
            'currency': data.get('currency', 'usd'),
            'payment_method_types': data.get('payment_method_types', ['card']),
        }
        
        # Add optional parameters if provided
        if data.get('receipt_email'):
            payment_params['receipt_email'] = data.get('receipt_email')
            
        if data.get('metadata'):
            payment_params['metadata'] = data.get('metadata')
            
        if data.get('description'):
            payment_params['description'] = data.get('description')
        
        # Create the Payment Intent
        payment_intent = stripe.PaymentIntent.create(**payment_params)
        
        return jsonify({
            'success': True,
            'clientSecret': payment_intent.client_secret,
            'paymentIntentId': payment_intent.id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

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
        return jsonify({"error": str(e)}), 400