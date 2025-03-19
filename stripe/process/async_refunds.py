import json
import time
import stripe
import logging
from config import Config
from utils.rabbitmq_utils import get_rabbitmq_connection, publish_message

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
# Set PIKA logging to WARNING
logging.getLogger("pika").setLevel(logging.WARNING)
# Configure our logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add formatter for cleaner logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

def process_refund_callback(ch, method, properties, body):
    try:
        refund_request = json.loads(body)
        logger.info("=============== Processing Refund ===============")
        logger.info(f"Refund request: {refund_request}")
        
        # Verify payment intent exists
        payment_intent = stripe.PaymentIntent.retrieve(refund_request['payment_intent_id'])
        logger.info(f"Found payment intent: {payment_intent.id}")

        # Create refund
        refund = stripe.Refund.create(
            payment_intent=refund_request['payment_intent_id'],
            amount=payment_intent.amount
        )
        logger.info(f"Refund created: {refund.id}, Status: {refund.status}")

        if refund.status == 'succeeded':
            # Publish email notification
            notification = {
                "type": "notification.email.refund",
                "data": {
                    "refund_id": refund.id,
                    "amount": refund.amount,
                    "customer_email": refund_request.get('customer_email'),
                    "payment_intent_id": payment_intent.id,
                    "timestamp": int(time.time())
                }
            }
            
            logger.info("=============== Publishing Email Notification ===============")
            logger.info(f"Notification data: {notification}")
            
            ch.basic_publish(
                exchange="notification",  # Changed from order_topic
                routing_key="notification.email.refund",
                body=json.dumps(notification)
            )
            logger.info(f"✅ Published refund notification for {refund.id}")
            
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Refund processing completed successfully")
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

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

def start_consuming():
    """Start consuming refund requests"""
    try:
        # Get connection
        connection = get_rabbitmq_connection()
        if not connection:
            logger.error("Failed to connect to RabbitMQ")
            return
            
        channel = connection.channel()
        
        # Declare queue
        channel.queue_declare(queue='stripe_refund_requests', durable=True)
        
        # Set up consumer
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue='stripe_refund_requests',
            on_message_callback=process_refund_callback
        )
        
        logger.info("Stripe service started consuming refund requests")
        channel.start_consuming()
        
    except Exception as e:
        logger.error(f"Error starting consumer: {str(e)}")
        if connection and not connection.is_closed:
            connection.close()