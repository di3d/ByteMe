import json
import time
import stripe
import logging
import pika
import sys
import os

# Fix imports by adding the correct paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from config import Config

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Get logger but don't reconfigure the root logger
logger = logging.getLogger(__name__)

# Import this function after we've setup the proper paths
from .message_queue import get_rabbitmq_connection

def process_refund_callback(ch, method, properties, body):
    try:
        refund_request = json.loads(body)
        logger.info("=============== Processing Refund ===============")
        logger.info(f"Refund request: {refund_request}")

        # Verify payment intent exists
        payment_intent = stripe.PaymentIntent.retrieve(refund_request['payment_intent_id'])
        logger.info(f"Found payment intent: {payment_intent.id}")

        # Process refund
        refund = stripe.Refund.create(
            payment_intent=refund_request['payment_intent_id'],
            amount=payment_intent.amount
        )
        logger.info(f"Refund created: {refund.id}, Status: {refund.status}")

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Refund processing completed successfully")

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def get_rabbitmq_connection_with_retry(retries=5, delay=5):
    """Attempt to establish a RabbitMQ connection with retry logic."""
    for attempt in range(retries):
        try:
            connection = get_rabbitmq_connection()
            if connection:
                return connection
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
        time.sleep(delay)
    raise Exception("Failed to connect to RabbitMQ after multiple attempts")

def start_consuming():
    try:
        connection = get_rabbitmq_connection_with_retry()
        channel = connection.channel()

        # Declare the refund request queue
        channel.queue_declare(queue='refund.request', durable=True)

        # Set prefetch count to 1 so workers only get one message at a time
        channel.basic_qos(prefetch_count=1)
        
        # Start consuming messages from the queue
        channel.basic_consume(queue='refund.request', on_message_callback=process_refund_callback)
        logger.info("Stripe service is consuming refund requests from 'refund.request' queue")
        channel.start_consuming()
    except Exception as e:
        logger.error(f"Error starting refund consumer: {str(e)}")
        # Add a retry mechanism if needed
        time.sleep(5)
        start_consuming()  # Restart the consumer