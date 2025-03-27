import pika
from email_service.config import EmailConfig
import logging
import atexit

# Configure logging
logger = logging.getLogger(__name__)

# Global connection and channel variables
connection = None
channel = None

def establish_connection():
    """
    Establish a new RabbitMQ connection
    
    Returns:
        tuple: Connection and channel objects
    """
    global connection, channel
    try:
        # Create connection parameters
        credentials = pika.PlainCredentials(
            EmailConfig.RABBITMQ_USER, 
            EmailConfig.RABBITMQ_PASS
        )
        parameters = pika.ConnectionParameters(
            host=EmailConfig.RABBITMQ_HOST, 
            port=EmailConfig.RABBITMQ_PORT, 
            credentials=credentials
        )
        
        # Establish connection
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Declare exchanges based on your existing setup
        channel.exchange_declare(exchange='order_topic', exchange_type='topic')
        channel.exchange_declare(exchange='notification', exchange_type='topic')
        channel.exchange_declare(exchange='payment', exchange_type='topic')
        channel.exchange_declare(exchange='stripe_exchange', exchange_type='topic')
        
        # Bind queues (copied from your existing logs)
        channel.queue_declare(queue='Order')
        channel.queue_bind(exchange='order_topic', queue='Order', routing_key='order.create')
        
        channel.queue_declare(queue='Delivery')
        channel.queue_bind(exchange='order_topic', queue='Delivery', routing_key='delivery.#')
        
        channel.queue_declare(queue='Parts')
        channel.queue_bind(exchange='order_topic', queue='Parts', routing_key='parts.#')
        
        channel.queue_declare(queue='EmailNotifications')
        channel.queue_bind(exchange='notification', queue='EmailNotifications', routing_key='notification.#')
        
        channel.queue_declare(queue='refund.request')
        channel.queue_bind(exchange='payment', queue='refund.request', routing_key='refund.request')
        
        logger.info("RabbitMQ connection and exchanges/queues established successfully")
        
        # Ensure connection is closed properly at exit
        atexit.register(close_connection)
        
        return connection, channel
    except Exception as e:
        logger.error(f"Error establishing RabbitMQ connection: {e}")
        raise

def close_connection():
    """
    Properly close the RabbitMQ connection
    """
    global connection, channel
    try:
        if channel and not channel.is_closed:
            channel.close()
        if connection and not connection.is_closed:
            connection.close()
        logger.info("RabbitMQ connection closed")
    except Exception as e:
        logger.error(f"Error closing RabbitMQ connection: {e}")

def check_setup():
    """
    Check and setup RabbitMQ connection and channel
    
    Returns:
        pika.adapters.blocking_connection.BlockingChannel: A RabbitMQ channel
    """
    global connection, channel
    
    try:
        # If no connection exists or is closed, create a new one
        if not connection or connection.is_closed:
            connection, channel = establish_connection()
        
        # If channel is closed, create a new one
        if not channel or channel.is_closed:
            channel = connection.channel()
        
        return channel
    except Exception as e:
        logger.error(f"Error in check_setup: {e}")
        raise

# Attempt to establish initial connection when module is imported
try:
    connection, channel = establish_connection()
except Exception as e:
    logger.error(f"Could not establish initial RabbitMQ connection: {e}")
    connection = None
    channel = None