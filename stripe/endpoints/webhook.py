from flask import jsonify, request
import stripe
import json
import time
from config import Config
from utils.rabbitmq_utils import publish_message
from endpoints.init import webhook_bp

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Handle Stripe webhook events.
    
    The webhook verifies the signature using the webhook secret and
    publishes events to RabbitMQ for processing by other services.
    
    Headers:
    - Stripe-Signature: (required) Webhook signature from Stripe
    
    Returns:
    - success: True if webhook was processed
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
        )
        
        # Convert to JSON for queue
        event_json = json.loads(json.dumps(event.data.object, default=str))
        
        # Publish webhook event to RabbitMQ
        webhook_message = {
            'event_type': event.type,
            'event_data': event_json,
            'timestamp': int(time.time())
        }
        
        publish_message(Config.QUEUE_WEBHOOKS, webhook_message)
        
        # Basic event logging
        print(f"Received webhook event: {event.type}")
        
        # Basic event processing
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            print(f"Payment succeeded for payment intent: {payment_intent.id}")
            
        return jsonify(success=True)
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400