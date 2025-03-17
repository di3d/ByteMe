import json
import time
import stripe
from config import Config
from utils.rabbitmq_utils import get_rabbitmq_connection, publish_message

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

def process_refund_callback(ch, method, properties, body):
    """
    Callback function to process refund requests from the queue.
    
    Args:
        ch: Channel
        method: Method
        properties: Properties
        body: Message body
    """
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
        
        publish_message(Config.QUEUE_REFUND_RESPONSES, response)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"Error processing refund request: {str(e)}")
        
        # Create error response
        error_response = {
            'success': False,
            'error': str(e),
            'order_id': refund_request.get('order_id') if 'refund_request' in locals() else None,
            'request_id': refund_request.get('request_id') if 'refund_request' in locals() else None,
            'timestamp': int(time.time())
        }
        
        # Publish error response
        publish_message(Config.QUEUE_REFUND_RESPONSES, error_response)
        
        # Acknowledge the message even on error
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_refund_worker():
    """
    Start a worker to process refund requests from the queue.
    """
    try:
        connection = get_rabbitmq_connection()
        if not connection:
            return
            
        channel = connection.channel()
        
        # Set prefetch count
        channel.basic_qos(prefetch_count=1)
        
        # Start consuming
        channel.basic_consume(
            queue=Config.QUEUE_REFUND_REQUESTS, 
            on_message_callback=process_refund_callback
        )
        
        print('Stripe service started consuming refund requests')
        channel.start_consuming()
        
    except Exception as e:
        print(f"Error in refund request consumer: {str(e)}")
        
        # Try to close the connection if it exists
        try:
            if connection and connection.is_open:
                connection.close()
        except:
            pass