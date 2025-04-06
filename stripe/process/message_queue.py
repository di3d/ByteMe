import pika
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from config import Config

# Use existing logger without reconfiguring
logger = logging.getLogger(__name__)

# Connection settings
amqp_host = Config.RABBITMQ_HOST
amqp_port = Config.RABBITMQ_PORT
amqp_user = Config.RABBITMQ_USER
amqp_password = Config.RABBITMQ_PASSWORD

# Define exchanges
EXCHANGES = {
    "order_topic": "topic",     # For order-related events
    "notification": "topic",    # For notifications/emails
    "payment": "topic",         # For payment/refund events
    "stripe_exchange": "topic"  # For Stripe-specific events
}

def get_rabbitmq_connection():
    """Create a new RabbitMQ connection"""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=amqp_host,
                port=amqp_port,
                credentials=pika.PlainCredentials(amqp_user, amqp_password),
                heartbeat=3600,
                blocked_connection_timeout=3600
            )
        )
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
        return None

def setup_all_queues():
    """Set up all queues needed by the system"""
    connection = get_rabbitmq_connection()
    if not connection:
        return False

    channel = connection.channel()

    # Declare all exchanges
    for exchange_name, exchange_type in EXCHANGES.items():
        try:
            channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_type,
                durable=True
            )
        except Exception as e:
            logger.error(f"Failed to declare exchange {exchange_name}: {str(e)}")

    connection.close()
    return True