import sys
import os

# Add the project root and /stripe directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../stripe')))

from flask import Flask, request, jsonify
from invokes import invoke_http  # Import from separate module
from config import Config
from amqp.amqp_setup import publish_message
import json
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

@app.route('/initiate-refund', methods=['POST'])
def initiate_refund():
    """
    Endpoint to initiate a refund and send a notification email.
    """
    data = request.get_json()

    # Validate required fields
    order_id = data.get('order_id')
    customer_id = data.get('customer_id')
    payment_intent_id = data.get('payment_intent_id')
    customer_email = data.get('customer_email')

    if not order_id or not customer_id or not payment_intent_id or not customer_email:
        logger.error("Missing required fields: order_id, customer_id, payment_intent_id, or customer_email")
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    # Fetch order details
    try:
        order_service_url = os.environ.get('ORDER_SERVICE_URL', 'http://127.0.0.1:5001')
        order_details = invoke_http(f"{order_service_url}/order/{order_id}", method="GET")
        if order_details.get("code", 200) >= 400:
            logger.error(f"Failed to retrieve order details: {order_details}")
            return jsonify({"success": False, "error": "Invalid order details"}), 400
    except Exception as e:
        logger.error(f"Error fetching order details: {str(e)}")
        return jsonify({"success": False, "error": "Failed to fetch order details"}), 500

    # Fetch parts details
    try:
        parts_service_url = os.environ.get('PARTS_SERVICE_URL', 'http://127.0.0.1:5002')
        parts_details = invoke_http(f"{parts_service_url}/parts/{order_id}", method="GET")
        if parts_details.get("code", 200) >= 400:
            logger.error(f"Failed to retrieve parts details: {parts_details}")
            return jsonify({"success": False, "error": "Invalid parts details"}), 400
    except Exception as e:
        logger.error(f"Error fetching parts details: {str(e)}")
        return jsonify({"success": False, "error": "Failed to fetch parts details"}), 500

    # Fetch customer details
    try:
        customer_service_url = os.environ.get('CUSTOMER_SERVICE_URL', 'http://127.0.0.1:5003')
        customer_details = invoke_http(f"{customer_service_url}/customer/{customer_id}", method="GET")
        if customer_details.get("code", 200) >= 400:
            logger.error(f"Failed to retrieve customer details: {customer_details}")
            return jsonify({"success": False, "error": "Invalid customer details"}), 400
    except Exception as e:
        logger.error(f"Error fetching customer details: {str(e)}")
        return jsonify({"success": False, "error": "Failed to fetch customer details"}), 500

    # Fetch payment intent details
    try:
        stripe_url = os.environ.get('STRIPE_SERVICE_URL', 'http://127.0.0.1:5000')
        payment_intent = invoke_http(f"{stripe_url}/payment-intent/{payment_intent_id}", method="GET")
        if payment_intent.get("code", 200) >= 400:
            logger.error(f"Failed to retrieve payment intent: {payment_intent}")
            return jsonify({"success": False, "error": payment_intent.get("message", "Unknown error")}), payment_intent.get("code", 500)

        if not payment_intent or payment_intent.get("status") != "succeeded":
            logger.error(f"Invalid payment intent: {payment_intent}")
            return jsonify({"success": False, "error": "Invalid payment intent or status"}), 400
    except Exception as e:
        logger.error(f"Error fetching payment intent: {str(e)}")
        return jsonify({"success": False, "error": "Failed to fetch payment intent"}), 500

    # Create refund message
    refund_message = {
        'payment_intent_id': payment_intent_id,
        'amount': payment_intent.get('amount'),
        'customer_email': customer_email
    }

    try:
        # Publish refund request to RabbitMQ
        logger.info(f"Publishing refund message: {refund_message}")
        publish_message('payment', 'refund.request', json.dumps(refund_message))
    except Exception as e:
        logger.error(f"Error publishing refund message: {str(e)}")
        return jsonify({"success": False, "error": "Failed to queue refund request"}), 500

    # Create delivery task
    delivery_message = {
        'order_id': order_id,
        'parts': parts_details.get('parts'),
        'customer_id': customer_id
    }

    try:
        publish_message('delivery', 'delivery.create', json.dumps(delivery_message))
        logger.info(f"Published delivery task: {delivery_message}")
    except Exception as e:
        logger.error(f"Error publishing delivery task: {str(e)}")
        return jsonify({"success": False, "error": "Failed to queue delivery task"}), 500

    # Send email notification
    email_message = {
        'type': 'notification.email.refund_initiated',
        'data': {
            'payment_intent_id': payment_intent_id,
            'amount': payment_intent.get('amount'),
            'currency': 'sgd',
            'customer_email': customer_email
        }
    }

    try:
        logger.info(f"Publishing email notification: {email_message}")
        publish_message('notification', 'notification.email', json.dumps(email_message))
    except Exception as e:
        logger.error(f"Error publishing email notification: {str(e)}")
        return jsonify({"success": False, "error": "Failed to send email notification"}), 500

    return jsonify({"success": True, "message": "Refund request queued successfully"})
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)