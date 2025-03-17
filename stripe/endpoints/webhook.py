from flask import jsonify, request
import stripe
import json
import time
from config import Config
from utils.rabbitmq_utils import publish_message, get_rabbitmq_connection
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
        
        # Process the event directly regardless of RabbitMQ availability
        print(f"Received webhook event: {event.type}")
        
        # Basic event processing
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            print(f"Payment succeeded for payment intent: {payment_intent.id}")
        
        # Only attempt to queue the event if RabbitMQ is available
        if get_rabbitmq_connection():
            # Convert to JSON for queue
            event_json = json.loads(json.dumps(event.data.object, default=str))
            
            # Publish webhook event to RabbitMQ
            webhook_message = {
                'event_type': event.type,
                'event_data': event_json,
                'timestamp': int(time.time())
            }
            
            publish_success = publish_message(Config.QUEUE_WEBHOOKS, webhook_message)
            if not publish_success:
                print(f"Warning: Failed to queue webhook event: {event.type}")
            
        return jsonify(success=True)
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 400