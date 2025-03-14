from flask import jsonify, request
import stripe
import json
import time
from config import Config
from utils.rabbitmq_utils import publish_message
from endpoints.init import refund_bp

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

@refund_bp.route('/refund', methods=['POST'])
def create_refund():
    """
    Process a refund synchronously.
    
    Request body parameters:
    - payment_intent_id: (required) Payment Intent ID to refund
    - amount: (optional) Amount to refund in cents, if omitted refunds full amount
    - reason: (optional) Reason for refund, default 'requested_by_customer'
    
    Returns:
    - success: True if successful
    - refund: Object containing refund details
      - id: Refund ID
      - amount: Refunded amount
      - status: Refund status
    """
    data = json.loads(request.data)
    try:
        if not data.get('payment_intent_id'):
            return jsonify({"error": "Payment intent ID is required"}), 400
        
        # Create refund parameters
        refund_params = {
            'payment_intent': data.get('payment_intent_id'),
            'reason': data.get('reason', 'requested_by_customer')
        }
        
        # Add amount if provided (for partial refunds)
        if data.get('amount'):
            refund_params['amount'] = data.get('amount')
            
        # Create the refund
        refund = stripe.Refund.create(**refund_params)
        
        return jsonify({
            'success': True,
            'refund': {
                'id': refund.id,
                'amount': refund.amount,
                'status': refund.status
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@refund_bp.route('/refund-async', methods=['POST'])
def create_refund_async():
    """
    Queue a refund to be processed asynchronously.
    
    Request body parameters:
    - payment_intent_id: (required) Payment Intent ID to refund
    - amount: (optional) Amount to refund in cents, if omitted refunds full amount
    - reason: (optional) Reason for refund, default 'requested_by_customer'
    - order_id: (optional) Order ID for tracking
    - request_id: (optional) Request ID for tracking, auto-generated if omitted
    
    Returns:
    - success: True if successful
    - message: Confirmation message
    - request_id: ID for tracking the refund request
    """
    data = json.loads(request.data)
    try:
        if not data.get('payment_intent_id'):
            return jsonify({"error": "Payment intent ID is required"}), 400
        
        # Create a refund request message
        refund_request = {
            'payment_intent_id': data.get('payment_intent_id'),
            'amount': data.get('amount'),
            'reason': data.get('reason', 'requested_by_customer'),
            'order_id': data.get('order_id'),
            'request_id': data.get('request_id', str(time.time())),
            'timestamp': int(time.time())
        }
        
        # Publish to the refund requests queue
        success = publish_message(Config.QUEUE_REFUND_REQUESTS, refund_request)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Refund request queued successfully',
                'request_id': refund_request['request_id']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to queue refund request'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@refund_bp.route('/refund-status/<request_id>', methods=['GET'])
def get_refund_status(request_id):
    """
    Check the status of an asynchronous refund request.
    
    Path parameters:
    - request_id: (required) The request ID from the initial refund request
    
    Returns:
    - success: True if refund was found
    - status: Refund status (pending, succeeded, failed, etc)
    - refund_id: Stripe refund ID if available
    - amount: Refunded amount if available
    """
    try:
        # In a production environment, you would check a database
        # where you've stored the refund responses from the queue
        
        # For demo purposes, we'll fetch directly from Stripe
        # This is a simplified implementation - in production you'd use a database
        payment_intent_id = request.args.get('payment_intent_id')
        
        if not payment_intent_id:
            return jsonify({
                "success": False,
                "error": "Payment intent ID is required as a query parameter"
            }), 400
        
        # List all refunds for this payment intent
        refunds = stripe.Refund.list(payment_intent=payment_intent_id)
        
        if not refunds.data:
            return jsonify({
                "success": False,
                "error": "No refunds found for this payment intent",
                "request_id": request_id
            }), 404
        
        # Return the most recent refund (you might want to filter by request_id in production)
        latest_refund = refunds.data[0]
        
        return jsonify({
            "success": True,
            "refund_id": latest_refund.id,
            "status": latest_refund.status,
            "amount": latest_refund.amount,
            "request_id": request_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400