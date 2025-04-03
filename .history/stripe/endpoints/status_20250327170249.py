from flask import jsonify
from config import Config
from endpoints.blueprint_registry import status_bp

@status_bp.route('/', methods=['GET'])
def home():
    """Return service status information."""
    return jsonify({
        'status': 'success',
        'message': 'Stripe Payment Microservice is running'
    })

@status_bp.route('/config', methods=['GET'])
def get_config():
    """Return Stripe publishable key for frontend initialization."""
    return jsonify({
        'stripePublishableKey': Config.STRIPE_PUBLISHABLE_KEY
    })