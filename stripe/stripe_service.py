from flask import Blueprint, request, jsonify
import stripe
import os

# Create Blueprint
bp = Blueprint('stripe', __name__)

@bp.route('/makePurchase', methods=['POST'])
def make_purchase():
    try:
        data = request.get_json()
        payment_intent = stripe.PaymentIntent.create(
            amount=data['amount'],  # amount in cents
            currency=data['currency'],
            description=data['description'],
            metadata={
                'customer_id': data['customerId'],
                'part_id': data['partId']
            }
        )
        
        # Save to your Order database
        # ...code to save to your database...
        
        return jsonify({
            'success': True,
            'clientSecret': payment_intent.client_secret,
            'orderId': '12345'  # Replace with actual order ID from your DB
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/makeRefund', methods=['POST'])
def make_refund():
    try:
        data = request.get_json()
        refund = stripe.Refund.create(
            payment_intent=data['paymentIntentId'],
            amount=data.get('amount')  # Optional for partial refunds
        )
        
        # Update your Order database
        # ...code to update refund status in database...
        
        # Send email confirmation
        # ...code to send email...
        
        return jsonify({
            'success': True,
            'refundId': refund.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
        
        # Handle different event types
        if event.type == 'payment_intent.succeeded':
            # Process successful payment
            payment_intent = event.data.object
            # Update order status in database
            print(f"Payment succeeded: {payment_intent.id}")
            
        elif event.type == 'payment_intent.payment_failed':
            # Handle failed payment
            payment_intent = event.data.object
            print(f"Payment failed: {payment_intent.id}")
            
        return jsonify(success=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 400