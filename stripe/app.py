from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import stripe
import logging
import threading
import sys
import os
from endpoints import checkout
from endpoints import payment
from endpoints import refund
from endpoints import status

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '/')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Update CORS configuration to explicitly allow requests from the frontend
CORS(app)

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Reinitialize RabbitMQ for refund requests
from process.message_queue import setup_all_queues

# Initialize AMQP for Stripe service
if not setup_all_queues():
    logger.error("Failed to setup Stripe AMQP queues")
    raise Exception("AMQP Setup Failed")

# Start refund processor in a separate thread
from process.refund_processor import start_consuming
threading.Thread(target=start_consuming, daemon=True).start()
logger.info("Stripe service started consuming refund requests")

# Register blueprints
from endpoints.blueprint_registry import checkout_bp, refund_bp, status_bp, payment_bp
app.register_blueprint(refund_bp)
app.register_blueprint(checkout_bp)
app.register_blueprint(status_bp)
app.register_blueprint(payment_bp)

@app.route('/debug/routes')
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': [method for method in rule.methods if method not in ['HEAD', 'OPTIONS']],
            'path': str(rule)
        })
    return jsonify(routes)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    logger.info("Stripe service started (RabbitMQ disabled)")
    app.run(host='0.0.0.0', port=5000, debug=True)