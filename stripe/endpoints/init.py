from flask import Blueprint

# Create Blueprints for each endpoint
status_bp = Blueprint('status', __name__)
checkout_bp = Blueprint('checkout', __name__)
payment_bp = Blueprint('payment', __name__)
refund_bp = Blueprint('refund', __name__)
webhook_bp = Blueprint('webhook', __name__)

# Import routes to register them with blueprints
from endpoints import status, checkout, payment, refund, webhook

def register_endpoints(app):
    """
    Register all endpoints with the Flask app
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(status_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(refund_bp)
    app.register_blueprint(webhook_bp)