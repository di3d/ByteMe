import stripe
import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Root route
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'success',
        'message': 'Stripe Payment Microservice is running'
    })

@app.route('/config', methods=['GET'])
def get_config():
    return jsonify({
        'stripePublishableKey': os.getenv('STRIPE_PUBLISHABLE_KEY')
    })

@app.route('/create-payment', methods=['POST'])
def create_payment():
    data = json.loads(request.data)
    try:
        # Validate the required amount field
        if not data.get('amount'):
            return jsonify({"error": "Amount is required"}), 400
            
        # Create a simple payment intent with just the amount
        payment_intent = stripe.PaymentIntent.create(
            payment_method_types=['card'],
            amount=data.get('amount'),  # Total price passed from other services
            currency=data.get('currency', 'sgd'),
            automatic_payment_methods={"enabled": False},
            metadata={
                'order_id': data.get('order_id', '')
            }
        )

        return jsonify({
            'success': True,
            'clientSecret': payment_intent.client_secret
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
        
        # Handle payment success
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            order_id = payment_intent.metadata.get('order_id')
            
            # Here you would normally notify your Order service
            # through an API call or message queue
            print(f"Payment succeeded for order: {order_id}")
            
        return jsonify(success=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)