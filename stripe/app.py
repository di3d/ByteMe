from flask import Flask
from flask_cors import CORS
from threading import Thread
import stripe
import sys
import time
from config import Config
from utils.rabbitmq_utils import setup_rabbitmq, get_rabbitmq_connection
from process.async_refunds import process_refund_callback, start_refund_worker
from endpoints.init import register_endpoints

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Flag to track RabbitMQ availability
rabbitmq_available = False

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

def check_rabbitmq():
    """Check if RabbitMQ is running and accessible"""
    print("Checking RabbitMQ connection...")
    try:
        connection = get_rabbitmq_connection()
        if connection:
            print("✅ Successfully connected to RabbitMQ")
            connection.close()
            return True
        else:
            print("❌ Failed to connect to RabbitMQ")
            print(f"   Attempted to connect to: {Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}")
            print(f"   Using credentials: {Config.RABBITMQ_USER}:{'*' * len(Config.RABBITMQ_PASSWORD)}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error checking RabbitMQ: {str(e)}")
        return False

if __name__ == '__main__':
    # Check if RabbitMQ is available
    print(f"Starting Stripe service with RabbitMQ at {Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}")
    
    rabbitmq_available = check_rabbitmq()
    
    # Initialize RabbitMQ queues if available
    if rabbitmq_available:
        queue_setup_success = setup_rabbitmq()
        if not queue_setup_success:
            print("⚠️ Failed to set up RabbitMQ queues")
            rabbitmq_available = False
    else:
        if Config.RABBITMQ_REQUIRED:
            print("❌ RabbitMQ is required but not available. Exiting...")
            sys.exit(1)
        else:
            print("⚠️ RabbitMQ is not available. Continuing with limited functionality.")
            print("   Async operations will fall back to synchronous processing.")
    
    # Create the Flask app
    app = create_app()
    
    # Only start the refund processor if RabbitMQ is available
    if rabbitmq_available:
        try:
            # Start the refund processor in a background thread
            refund_processor_thread = Thread(target=start_refund_worker)
            refund_processor_thread.daemon = True
            refund_processor_thread.start()
            print("✅ Refund processor thread started")
        except Exception as e:
            print(f"❌ Failed to start refund processor: {str(e)}")
            print("Async refund processing will be disabled")
    else:
        print("⚠️ Running with limited functionality:")
        print("  - Synchronous refunds will work")
        print("  - Asynchronous refunds will fall back to synchronous processing")
        print("  - Webhook events won't be queued for background processing")
    
    # Start Flask app - change host parameter
    app.run(host='127.0.0.1', port=5000, debug=False)  # Only accessible locally