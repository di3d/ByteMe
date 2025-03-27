import logging
from flask import jsonify, request
import stripe
import json
import time
from config import Config
from utils.rabbitmq_utils import publish_message, get_rabbitmq_connection
from endpoints.init import refund_bp
import sys
import os

# Add path for AMQP setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../amqp')))
import amqp_setup

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
def refund_async():
    try:
        data = request.get_json()
        logger.info(f"Received refund request for: {data.get('payment_intent_id')}")
        
        # Verify payment intent first
        payment_intent = stripe.PaymentIntent.retrieve(data['payment_intent_id'])
        logger.info(f"Found payment intent: {payment_intent.id}, Status: {payment_intent.status}")

        # Create message for queue
        message = {
            'payment_intent_id': data['payment_intent_id'],
            'amount': payment_intent.amount,
            'customer_email': data.get('customer_email'),
            'request_id': str(time.time())
        }
        
        # Publish to queue
        amqp_setup.channel.basic_publish(
            exchange='stripe_exchange',
            routing_key='refund.request',
            body=json.dumps(message)
        )
        
        return jsonify({
            "success": True,
            "message": "Refund request received and processing",
            "request_id": message['request_id'],
            "payment_intent": payment_intent.id,
            "amount": payment_intent.amount
        })

    except Exception as e:
        logger.error(f"Error in refund request: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def process_refund_synchronously(data):
    """
    Process a refund synchronously (as fallback when RabbitMQ is unavailable)
    
    Args:
        data (dict): Request data containing payment_intent_id, amount, etc.
        
    Returns:
        Response: Flask JSON response
    """
    try:
        # Create refund parameters
        refund_params = {
            'payment_intent': data.get('payment_intent_id'),
            'reason': data.get('reason', 'requested_by_customer')
        }
        
        # Add amount if provided for partial refunds
        if data.get('amount'):
            refund_params['amount'] = data.get('amount')
            
        # Process the refund directly through Stripe
        refund = stripe.Refund.create(**refund_params)
        
        return jsonify({
            'success': True,
            'message': 'Refund processed synchronously (RabbitMQ unavailable)',
            'refund': {
                'id': refund.id,
                'amount': refund.amount,
                'status': refund.status
            },
            'request_id': data.get('request_id', str(time.time()))
        })
    except Exception as e:
        return jsonify({'error': f"Synchronous refund failed: {str(e)}"}), 400

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