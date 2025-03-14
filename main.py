import stripe
import json
import os
import time
import pika
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv, find_dotenv
from threading import Thread

# Load environment variables
load_dotenv(find_dotenv())

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        os.getenv('RABBITMQ_USER', 'guest'), 
        os.getenv('RABBITMQ_PASSWORD', 'guest')
    )
    parameters = pika.ConnectionParameters(
        host=os.getenv('RABBITMQ_HOST', 'localhost'),
        port=int(os.getenv('RABBITMQ_PORT', 5672)),
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

def setup_rabbitmq():
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declare queues
        channel.queue_declare(queue='stripe_refund_requests', durable=True)
        channel.queue_declare(queue='stripe_refund_responses', durable=True)
        channel.queue_declare(queue='stripe_webhooks', durable=True)
        
        connection.close()
        print("RabbitMQ queues initialized")
    except Exception as e:
        print(f"Error setting up RabbitMQ: {str(e)}")
        
def publish_message(queue_name, message):
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json',
                correlation_id=message.get('correlation_id', ''),
                message_id=str(time.time())
            )
        )
        
        connection.close()
        return True
    except Exception as e:
        print(f"RabbitMQ publish error: {str(e)}")
        return False

# Consumer for processing refund requests from the queue
def process_refund_requests():
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        def callback(ch, method, properties, body):
            try:
                refund_request = json.loads(body)
                print(f"Processing refund request: {refund_request}")
                
                # Extract refund details
                payment_intent_id = refund_request.get('payment_intent_id')
                amount = refund_request.get('amount')
                reason = refund_request.get('reason', 'requested_by_customer')
                order_id = refund_request.get('order_id')
                request_id = refund_request.get('request_id')
                
                # Process the refund through Stripe
                refund = stripe.Refund.create(
                    payment_intent=payment_intent_id,
                    amount=amount,
                    reason=reason
                )
                
                # Publish the result to the response queue
                response = {
                    'success': True,
                    'refund_id': refund.id,
                    'amount': refund.amount,
                    'status': refund.status,
                    'order_id': order_id,
                    'request_id': request_id,
                    'timestamp': int(time.time())
                }
                
                publish_message('stripe_refund_responses', response)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                error_response = {
                    'success': False,
                    'error': str(e),
                    'order_id': refund_request.get('order_id') if 'refund_request' in locals() else None,
                    'request_id': refund_request.get('request_id') if 'refund_request' in locals() else None,
                    'timestamp': int(time.time())
                }
                publish_message('stripe_refund_responses', error_response)
                ch.basic_ack(delivery_tag=method.delivery_tag)
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='stripe_refund_requests', on_message_callback=callback)
        
        print('Stripe service started consuming refund requests')
        channel.start_consuming()
        
    except Exception as e:
        print(f"Error in refund request consumer: {str(e)}")

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

# Add this new route to your Flask server

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = json.loads(request.data)
    try:
        # Validate minimum required fields
        if not data.get('amount'):
            return jsonify({"error": "Amount is required"}), 400
            
        # Create a list of line items for the checkout session
        line_items = [{
            'price_data': {
                'currency': data.get('currency', 'sgd'),
                'product_data': {
                    'name': 'Custom PC Build',
                    'description': f'Order ID: {data.get("order_id", "")}',
                },
                'unit_amount': data.get('amount'),
            },
            'quantity': 1,
        }]
        
        # Create a Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=data.get('success_url', request.host_url + 'success'),
            cancel_url=data.get('cancel_url', request.host_url + 'checkout?canceled=true'),
            metadata={
                'order_id': data.get('order_id', '')
            },
            customer_email=data.get('customer_email'),  # Pre-fill customer email if available
        )
        
        return jsonify({'url': checkout_session.url})
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
        
        # Publish webhook event to RabbitMQ
        webhook_message = {
            'event_type': event.type,
            'event_data': json.loads(json.dumps(event.data.object, default=str)),
            'timestamp': int(time.time())
        }
        
        publish_message('stripe_webhooks', webhook_message)
        
        # Also process directly
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            order_id = payment_intent.metadata.get('order_id')
            print(f"Payment succeeded for order: {order_id}")
            
        return jsonify(success=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# HTTP endpoint for refunds    
@app.route('/refund', methods=['POST'])
def create_refund():
    data = json.loads(request.data)
    try:
        if not data.get('payment_intent_id'):
            return jsonify({"error": "Payment intent ID is required"}), 400
            
        refund = stripe.Refund.create(
            payment_intent=data.get('payment_intent_id'),
            amount=data.get('amount'),  # Optional for partial refunds
            reason=data.get('reason', 'requested_by_customer')
        )
        
        return jsonify({
            'success': True,
            'refund': {
                'id': refund.id,
                'amount': refund.amount,
                'status': refund.status
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# New endpoint to initiate AMQP refund (fire and forget)
@app.route('/refund-async', methods=['POST'])
def create_refund_async():
    data = json.loads(request.data)
    try:
        if not data.get('payment_intent_id'):
            return jsonify({"error": "Payment intent ID is required"}), 400
        
        # Create a refund request message
        refund_request = {
            'payment_intent_id': data.get('payment_intent_id'),
            'amount': data.get('amount'),  # Optional for partial refunds
            'reason': data.get('reason', 'requested_by_customer'),
            'order_id': data.get('order_id'),
            'request_id': data.get('request_id', str(time.time())),
            'timestamp': int(time.time())
        }
        
        # Publish to the refund requests queue
        success = publish_message('stripe_refund_requests', refund_request)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Refund request queued successfully',
                'request_id': refund_request['request_id']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to queue refund request'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Initialize RabbitMQ
    setup_rabbitmq()
    
    # Start the refund request consumer in a background thread
    refund_consumer = Thread(target=process_refund_requests)
    refund_consumer.daemon = True
    refund_consumer.start()
    
    # Start Flask app
    app.run(port=5000, debug=False)  # Using debug=False when running with threads
    
    
# Add this endpoint to your Flask server

@app.route('/checkout-session', methods=['GET'])
def get_checkout_session():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({"error": "Session ID is required"}), 400
    
    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Extract relevant information
        response_data = {
            "payment_intent": session.payment_intent,
            "amount_total": session.amount_total,
            "currency": session.currency,
            "customer_email": session.customer_email,
            "payment_status": session.payment_status,
            "metadata": session.metadata
        }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400