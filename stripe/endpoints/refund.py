import logging
from flask import jsonify, request
import stripe
import json
import time
from config import Config
from endpoints.blueprint_registry import refund_bp
import sys
import os

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Setup logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@refund_bp.route('/refund-async', methods=['POST'])
def refund_async():
    try:
        data = request.get_json()
        logger.info(f"Received refund request for: {data.get('payment_intent_id')}")
        
        # Verify payment intent first
        payment_intent = stripe.PaymentIntent.retrieve(data['payment_intent_id'])
        logger.info(f"Found payment intent: {payment_intent.id}, Status: {payment_intent.status}")
        
        return jsonify({
            "success": True,
            "message": "Refund request received and processing",
            "payment_intent": payment_intent.id,
            "amount": payment_intent.amount
        })
    except Exception as e:
        logger.error(f"Error in refund request: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@refund_bp.route('/refund-status/<request_id>', methods=['GET'])
def get_refund_status(request_id):
    try:
        # Get payment intent ID from request ID (you'll need to implement this mapping)
        payment_intent_id = request_id  # In this example, we're using the payment intent ID directly
        
        # Get all refunds for this payment intent
        refunds = stripe.Refund.list(payment_intent=payment_intent_id)
        
        if not refunds.data:
            return jsonify({
                "success": False,
                "error": "No refunds found for this payment intent",
                "request_id": request_id
            }), 404
        
        # Return the most recent refund
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