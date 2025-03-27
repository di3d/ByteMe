from flask import Flask
from flask_cors import CORS
from config import Config
import stripe
import logging
import threading
import sys
import os

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '/')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Update CORS configuration to explicitly allow requests from the frontend
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

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

if __name__ == "__main__":
    logger.info("Stripe service started (RabbitMQ disabled)")
    app.run(port=5000, debug=True)