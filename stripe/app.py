from flask import Flask
from flask_cors import CORS
from config import Config
import stripe
from utils.rabbitmq_utils import setup_stripe_queues
from process.async_refunds import start_consuming
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Initialize AMQP for Stripe service
if not setup_stripe_queues():
    logger.error("Failed to setup Stripe AMQP queues")
    raise Exception("AMQP Setup Failed")

# Register blueprints
from endpoints.checkout import checkout_bp
from endpoints.refund import refund_bp
app.register_blueprint(checkout_bp)
app.register_blueprint(refund_bp)

if __name__ == "__main__":
    # Start refund processor in a separate thread
    threading.Thread(target=start_consuming, daemon=True).start()
    logger.info("Stripe service started consuming refund requests")
    
    # Start Flask app
    app.run(port=5000, debug=True)