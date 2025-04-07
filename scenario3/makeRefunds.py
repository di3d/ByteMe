import sys
import os

# Add the project root and /stripe directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../stripe')))

# RabbitMQ settings
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', '5673'))

from flask import Flask, request, jsonify
from invokes import invoke_http
from config import Config
from amqp.amqp_setup import publish_message
import json
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
CUSTOMER_URL = os.environ.get('CUSTOMER_SERVICE_URL', 'http://customer:5001')
STRIPE_URL = os.environ.get('STRIPE_SERVICE_URL', 'http://stripe:5000')
DELIVERY_URL = os.environ.get('DELIVERY_SERVICE_URL', 'http://delivery:5003')
ORDER_URL = os.environ.get('ORDER_SERVICE_URL', 'http://order:5002')
OUTSYSTEMS_URL = 'https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI'

def safe_publish(exchange, routing_key, message):
    """Safely publish a message to RabbitMQ with error handling"""
    try:
        publish_message(exchange, routing_key, message)
        logger.info(f"✅ Message published to {exchange}.{routing_key}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to publish message to {exchange}.{routing_key}: {str(e)}")
        return False

@app.route('/initiate-refund', methods=['POST'])
def initiate_refund():
    data = request.get_json()
    logger.info(f"Received refund request: {data}")

    # Validate required fields
    order_id = data.get('order_id')
    customer_id = data.get('customer_id')

    if not order_id or not customer_id:
        logger.error("Missing required fields: order_id or customer_id")
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        # Step 1: Get customer details from customer service
        logger.info(f"1️⃣ Fetching customer details for customer ID: {customer_id}")
        customer_response = invoke_http(f"{CUSTOMER_URL}/customer/{customer_id}", method='GET')
        
        if customer_response.get("code") != 200:
            logger.error(f"Failed to get customer details: {customer_response}")
            return jsonify({"success": False, "error": "Failed to get customer details"}), 400
        
        customer_email = customer_response.get("data", {}).get("email")
        customer_address = customer_response.get("data", {}).get("address")
        
        logger.info(f"Customer email: {customer_email}, address: {customer_address}")
        
        # Step 2: Get order details including parts list and payment intent ID
        logger.info(f"2️⃣ Fetching order details for order ID: {order_id}")
        order_response = invoke_http(f"{ORDER_URL}/order/{order_id}", method='GET')
        
        if order_response.get("code") != 200:
            logger.error(f"Failed to get order details: {order_response}")
            return jsonify({"success": False, "error": "Failed to get order details"}), 400
        
        order_data = order_response.get("data", {})
        parts_list = order_data.get("parts_list", [])
        payment_intent_id = order_id  # In your system, the order_id is the payment_intent_id
        
        # Step 3: Fetch payment intent details
        logger.info(f"3️⃣ Verifying payment intent: {payment_intent_id}")
        payment_intent_response = invoke_http(f"{STRIPE_URL}/payment-intent/{payment_intent_id}", method="GET")
        
        if payment_intent_response.get("code", 200) >= 400:
            logger.error(f"Failed to retrieve payment intent: {payment_intent_response}")
            return jsonify({"success": False, "error": payment_intent_response.get("message", "Unknown error")}), payment_intent_response.get("code", 500)

        # Extract payment amount
        payment_amount = payment_intent_response.get("data", {}).get("amount", 0)
        
        # Step 4: Initiate refund via Stripe
        logger.info(f"4️⃣ Initiating refund for payment: {payment_intent_id}")
        refund_message = {
            'payment_intent_id': payment_intent_id,
            'amount': payment_amount,
            'customer_email': customer_email
        }
        
        if not safe_publish('payment', 'refund.request', json.dumps(refund_message)):
            return jsonify({"success": False, "error": "Failed to initiate refund"}), 500
            
        # Step 5: Send email notification
        logger.info(f"5️⃣ Sending refund email notification to: {customer_email}")
        email_message = {
            'type': 'notification.email.refund_initiated',
            'data': {
                'payment_intent_id': payment_intent_id,
                'amount': payment_amount,
                'currency': 'sgd',
                'customer_email': customer_email
            }
        }
        
        if not safe_publish('notification', 'notification.email', json.dumps(email_message)):
            logger.warning("⚠️ Failed to send email notification, but continuing with refund process")
            
        # Step 6: Update inventory for each part
        logger.info(f"6️⃣ Restoring inventory for {len(parts_list)} parts")
        for part_id in parts_list:
            # Convert string to integer if needed
            component_id = part_id if isinstance(part_id, int) else int(part_id)
            
            # Increase stock by 1
            update_url = f"{OUTSYSTEMS_URL}/UpdateComponentStock?ComponentId={component_id}&QuantityChange=1"
            logger.info(f"Updating stock for component {component_id}: {update_url}")
            
            try:
                stock_response = invoke_http(update_url, method='POST')
                logger.info(f"Stock update response for part {component_id}: {stock_response}")
            except Exception as e:
                logger.error(f"Failed to update stock for part {component_id}: {str(e)}")
                # Continue with other parts even if one fails
        
        # Step 7: Create delivery record for returned items
        logger.info(f"7️⃣ Creating return delivery record")
        delivery_data = {
            "order_id": order_id,
            "customer_id": customer_id,
            "parts_list": parts_list,
            "address": customer_address
        }
        
        try:
            delivery_response = invoke_http(f"{DELIVERY_URL}/delivery", method='POST', json=delivery_data)
            logger.info(f"Delivery response: {delivery_response}")
        except Exception as e:
            logger.error(f"Failed to create delivery record: {str(e)}")
            # Continue even if delivery creation fails
        
        # Step 8: Update order status to "refunded"
        logger.info(f"8️⃣ Updating order status to 'refunded'")
        try:
            status_update_response = invoke_http(
                f"{ORDER_URL}/order/{order_id}/status",
                method='PUT',
                json={"status": "refunded"}
            )
            
            if status_update_response.get("code") == 200:
                logger.info(f"Order status updated successfully: {order_id} → refunded")
            else:
                logger.error(f"Failed to update order status: {status_update_response}")
                # Continue even if status update fails
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            # Continue even if status update fails
        
        return jsonify({
            "success": True, 
            "message": "Refund process completed successfully",
            "order_id": order_id,
            "customer_id": customer_id,
            "refund_amount": payment_amount
        })

    except Exception as e:
        logger.error(f"Error in refund process: {str(e)}")
        return jsonify({"success": False, "error": f"Failed to process refund: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)