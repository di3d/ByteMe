import stripe
import json
import setup_payment as setup
import os

from stripe_service import bp as stripe_bp
from inventory import Inventory
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Fixed key name
app.register_blueprint(stripe_bp, url_prefix='/api/payments')
# Root route
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'success',
        'message': 'PC Store API is running'
    })

@app.route('/config')
def get_config():
    return jsonify({
        'stripePublishableKey': os.getenv('STRIPE_PUBLISHABLE_KEY'),
        'stripeCountry': os.getenv('STRIPE_ACCOUNT_COUNTRY') or 'US',
        'country': 'US',
        'currency': 'usd',
        'paymentMethods': os.getenv('PAYMENT_METHODS').split(', ') if os.getenv('PAYMENT_METHODS') else ['card'],
        'shippingOptions': [
            {
                'id': 'free',
                'label': 'Free Shipping',
                'detail': 'Delivery within 7-10 business days',
                'amount': 0,
            },
            {
                'id': 'standard',
                'label': 'Standard Shipping',
                'detail': 'Delivery within 3-5 business days',
                'amount': 999,
            },
            {
                'id': 'express',
                'label': 'Express Shipping',
                'detail': 'Delivery within 2 business days',
                'amount': 1999,
            },
            {
                'id': 'overnight',
                'label': 'Overnight Shipping',
                'detail': 'Next day delivery (order before 2pm)',
                'amount': 2999,
            }
        ]
    })

@app.route('/products', methods=['GET'])
def get_products():
    products = Inventory.list_products()
    if Inventory.products_exist(products):
        return jsonify(products)
    else:
        # Create Products for our Stripe store if we haven't already.
        setup.create_data()
        products = Inventory.list_products()
        return jsonify(products)

# Add payment intent endpoints
@app.route('/payment_intents', methods=['POST'])
def make_payment_intent():
    # Creates a new PaymentIntent with items from the cart.
    data = json.loads(request.data)
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=Inventory.calculate_payment_amount(items=data['items']),
            currency=data['currency'],
            payment_method_types=['card']
        )

        return jsonify({'paymentIntent': payment_intent})
    except Exception as e:
        return jsonify({"error": str(e)}), 403

@app.route('/payment_intents/<string:id>/shipping_change', methods=['POST'])
def update_payment_intent(id):
    data = json.loads(request.data)
    amount = Inventory.calculate_payment_amount(items=data['items'])
    amount += Inventory.get_shipping_cost(data['shippingOption']['id'])
    try:
        payment_intent = stripe.PaymentIntent.modify(
            id,
            amount=amount
        )

        return jsonify({'paymentIntent': payment_intent})
    except Exception as e:
        return jsonify({"error": str(e)}), 403

if __name__ == '__main__':
    app.run(port=3000, debug=True)