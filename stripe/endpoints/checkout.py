from flask import jsonify, request
import stripe
import json
from config import Config
from endpoints.init import checkout_bp

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

@checkout_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """
    Create a new Stripe Checkout Session.
    
    Request body parameters:
    - amount: (required) Amount in cents
    - line_items: (optional) Custom line items array
    - currency: (optional) 3-letter currency code, default 'usd'
    - product_name: (optional) Name of the product
    - product_description: (optional) Description of the product
    - quantity: (optional) Quantity of items, default 1
    - payment_method_types: (optional) Array of payment methods, default ['card']
    - mode: (optional) Checkout mode, default 'payment'
    - success_url: (optional) URL to redirect on success
    - cancel_url: (optional) URL to redirect on cancel
    - metadata: (optional) Additional metadata
    - customer_email: (optional) Pre-fill customer email
    - shipping_address_collection: (optional) Shipping address collection config
    - billing_address_collection: (optional) Billing address collection config
    
    Returns:
    - url: Checkout session URL
    """
    data = json.loads(request.data)
    try:
        # Validate minimum required fields
        if not data.get('amount') and not data.get('line_items'):
            return jsonify({"error": "Either amount or line_items is required"}), 400
            
        # Create line items from the request
        line_items = []
        
        # If line items are provided directly, use them
        if data.get('line_items'):
            line_items = data.get('line_items')
        # Otherwise, create a generic line item
        else:
            line_items = [{
                'price_data': {
                    'currency': data.get('currency', 'usd'),
                    'product_data': {
                        'name': data.get('product_name', 'Product'),
                        'description': data.get('product_description', '')
                    },
                    'unit_amount': data.get('amount'),
                },
                'quantity': data.get('quantity', 1),
            }]
        
        # Create session parameters
        session_params = {
            'payment_method_types': data.get('payment_method_types', ['card']),
            'line_items': line_items,
            'mode': data.get('mode', 'payment'),
            'success_url': data.get('success_url', Config.DEFAULT_SUCCESS_URL),
            'cancel_url': data.get('cancel_url', Config.DEFAULT_CANCEL_URL),
        }
        
        # Add optional parameters if provided
        if data.get('metadata'):
            session_params['metadata'] = data.get('metadata')
        
        if data.get('customer_email'):
            session_params['customer_email'] = data.get('customer_email')
            
        if data.get('shipping_address_collection'):
            session_params['shipping_address_collection'] = data.get('shipping_address_collection')
            
        if data.get('billing_address_collection'):
            session_params['billing_address_collection'] = data.get('billing_address_collection')
        
        # Create the Checkout Session
        checkout_session = stripe.checkout.Session.create(**session_params)
        
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

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