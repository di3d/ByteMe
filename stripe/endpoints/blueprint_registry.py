from flask import Blueprint

# Create blueprints with proper URL prefixes
checkout_bp = Blueprint('checkout', __name__)  # Remove url_prefix
payment_bp = Blueprint('payment', __name__)    # Remove url_prefix 
refund_bp = Blueprint('refund', __name__)      # Remove url_prefix
status_bp = Blueprint('status', __name__)      # Remove url_prefix