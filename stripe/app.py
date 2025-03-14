from flask import Flask
from flask_cors import CORS
from threading import Thread
import stripe
from config import Config
from utils.rabbitmq_utils import setup_rabbitmq
from process.async_refunds import process_refund_callback, start_refund_worker
from endpoints.init import register_endpoints

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: The configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Register all endpoint blueprints
    register_endpoints(app)
    
    return app

if __name__ == '__main__':
    # Initialize RabbitMQ
    setup_rabbitmq()
    
    # Create the Flask app
    app = create_app()
    
    # Start the refund processor in a background thread
    refund_processor_thread = Thread(target=start_refund_worker)
    refund_processor_thread.daemon = True
    refund_processor_thread.start()
    
    # Start Flask app
    app.run(port=5000, debug=False)  # Using debug=False when running with threads