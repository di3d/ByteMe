import sys
import os

# Add the project root and /stripe directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../stripe')))

from flask import Flask, request, jsonify
import requests
from config import Config
from amqp.amqp_setup import publish_message
import json
from flask_cors import CORS
import logging

SUPPORTED_HTTP_METHODS = set([
    "GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"
])

def invoke_http(url, method='GET', json=None, **kwargs):
    """
    A simple wrapper for HTTP requests.
    """
    try:
        if method.upper() in SUPPORTED_HTTP_METHODS:
            response = requests.request(method, url, json=json, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        else:
            raise ValueError(f"HTTP method {method} unsupported.")
    except requests.exceptions.RequestException as e:
        return {"code": 500, "message": f"HTTP request failed: {str(e)}"}

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/initiate-refund', methods=['POST'])
def initiate_refund():
    """
    Endpoint to initiate a refund and send a notification email.
    """
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        customer_email = data.get('customer_email')
        if not payment_intent_id or not customer_email:
            logger.error("Missing required fields: payment_intent_id or customer_email")
            return jsonify({"success": False, "error": "Missing required fields: payment_intent_id or customer_email"}), 400

        # Get the Stripe service URL from environment or use default
        stripe_url = os.environ.get('STRIPE_SERVICE_URL', 'http://127.0.0.1:5000')
        
        logger.info(f"Retrieving payment intent: {payment_intent_id}")
        payment_intent = invoke_http(f"{stripe_url}/payment-intent/{payment_intent_id}", method="GET")

        # Check if the payment intent retrieval was successful
        if not payment_intent or payment_intent.get("status") != "succeeded":
            logger.error(f"Invalid payment intent: {payment_intent}")
            return jsonify({"success": False, "error": "Invalid payment intent or status"}), 400

        # Create message for refund queue
        refund_message = {
            'payment_intent_id': payment_intent_id,
            'amount': payment_intent.get('amount'),
            'customer_email': customer_email
        }

        # Publish refund request to RabbitMQ
        logger.info(f"Publishing refund message: {refund_message}")
        publish_message('payment', 'refund.request', json.dumps(refund_message))

        # Create message for email notification
        email_message = {
            'type': 'notification.email.refund_initiated',
            'data': {
                'payment_intent_id': payment_intent_id,
                'amount': payment_intent.get('amount'),
                'currency': 'sgd',
                'customer_email': customer_email
            }
        }

        # Publish email notification to RabbitMQ
        logger.info(f"Publishing email notification: {email_message}")
        publish_message('notification', 'notification.email', json.dumps(email_message))

        return jsonify({"success": True, "message": "Refund request queued successfully"})
    except Exception as e:
        logger.error(f"Error in /initiate-refund: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)