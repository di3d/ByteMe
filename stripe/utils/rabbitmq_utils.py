import pika
import json
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_rabbitmq_connection():
    """Create a new RabbitMQ connection"""
    try:
        return pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5672,
                heartbeat=3600,
                blocked_connection_timeout=3600
            )
        )
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
        return None

def setup_stripe_queues():
    """Set up Stripe-specific queues"""
    try:
        connection = get_rabbitmq_connection()
        if not connection:
            return False
            
        channel = connection.channel()
        
        # Declare Stripe-specific exchange
        channel.exchange_declare(
            exchange='stripe_exchange',  # Changed from payment_exchange
            exchange_type='topic',
            durable=True
        )
        
        # Only Stripe-specific queues
        stripe_queues = {
            'stripe_refund_requests': 'refund.request',
            'stripe_refund_responses': 'refund.response',
            'stripe_notifications': 'notification.payment'
        }
        
        # Set up each queue
        for queue_name, routing_key in stripe_queues.items():
            channel.queue_declare(queue=queue_name, durable=True)
            channel.queue_bind(
                exchange='stripe_exchange',
                queue=queue_name,
                routing_key=routing_key
            )
            logger.info(f"Initialized Stripe queue: {queue_name}")
        
        connection.close()
        logger.info("Stripe queue setup completed")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup Stripe queues: {str(e)}")
        return False

def publish_message(routing_key, message):
    """Publish message to Stripe exchange"""
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        channel.basic_publish(
            exchange='stripe_exchange',  # Changed from payment_exchange
            routing_key=routing_key,
            body=json.dumps(message)
        )
        
        connection.close()
        return True
    except Exception as e:
        logger.error(f"Failed to publish message: {str(e)}")
        return False