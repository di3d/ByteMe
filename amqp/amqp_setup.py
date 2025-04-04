# unified_amqp_setup.py
import pika
import os
from os import environ
import sys
import os
import logging
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../stripe')))
# from amqp.config import Config
from config import Config
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection settings
# Force RabbitMQ to use IPv4 explicitly
amqp_host = 'rabbitmq'  # Updated to use the Docker service name
amqp_port = Config.RABBITMQ_PORT or 5672
amqp_user = Config.RABBITMQ_USER or 'guest'
amqp_password = Config.RABBITMQ_PASSWORD or 'guest'

# Define exchanges
EXCHANGES = {
    "order_topic": "topic",     # For order-related events
    "notification": "topic",    # For notifications/emails
    "payment": "topic"          # For payment/refund events
}

"""
This function creates a channel (connection) and establishes connection with AMQP server
"""
def get_rabbitmq_connection(max_retries=10, retry_delay=5):
    retries = 0
    while retries < max_retries:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=amqp_host,
                    port=amqp_port,
                    heartbeat=3600,
                    blocked_connection_timeout=3600,
                ))
            logger.info(f"Successfully connected to RabbitMQ after {retries} retries")
            return connection
        except Exception as e:
            retries += 1
            logger.error(f"Failed to connect to RabbitMQ (attempt {retries}/{max_retries}): {str(e)}")
            if retries < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    logger.error(f"Failed to connect to RabbitMQ after {max_retries} attempts")
    return None
    
    
def create_channel():
    """Create a channel and ensure all exchanges exist"""
    connection = get_rabbitmq_connection()
    if not connection:
        return None, None
        
    channel = connection.channel()
    
    # Declare all exchanges
    for exchange_name, exchange_type in EXCHANGES.items():
        try:
            channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_type,
                durable=True
            )
            logger.info(f"Declared exchange: {exchange_name}")
        except Exception as e:
            logger.error(f"Failed to declare exchange {exchange_name}: {str(e)}")
    
    return connection, channel


def create_queue(channel, exchange_name, queue_name, routing_key):
    """Create a queue and bind it to an exchange"""
    try:
        logger.info(f"Binding queue: {queue_name} to exchange: {exchange_name} with routing key: {routing_key}")
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        return True
    except Exception as e:
        logger.error(f"Failed to create queue {queue_name}: {str(e)}")
        return False


def setup_all_queues():
    """Set up all queues needed by the system"""
    connection, channel = create_channel()
    if not channel:
        return False
    
    try:
        # Order-related queues
        create_queue(channel, "order_topic", "Order", "order.create")
        create_queue(channel, "order_topic", "Delivery", "delivery.#")
        create_queue(channel, "order_topic", "Parts", "parts.#")
        
        # Notification queues
        create_queue(channel, "notification", "EmailNotifications", "notification.#")
        
        # Payment/refund queues - THIS IS THE CRITICAL PART
        create_queue(channel, "payment", "refund.request", "refund.request")
        
        connection.close()
        return True
    except Exception as e:
        logger.error(f"Failed to setup queues: {str(e)}")
        if connection and connection.is_open:
            connection.close()
        return False


def publish_message(exchange_name, routing_key, message):
    """Publish a message to an exchange"""
    try:
        connection = get_rabbitmq_connection()
        if not connection:
            raise Exception("No RabbitMQ connection available")

        channel = connection.channel()
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )
        logger.info(f"Message published to exchange '{exchange_name}' with routing key '{routing_key}': {message}")
        connection.close()
    except Exception as e:
        logger.error(f"Failed to publish message: {str(e)}")

def check_setup():
    """Check if the RabbitMQ setup is working"""
    connection = get_rabbitmq_connection()
    if not connection:
        return False
    
    connection.close()
    return True

# Initialize when module is imported
setup_all_queues()

if __name__ == "__main__":
    # Run the setup
    if setup_all_queues():
        logger.info("AMQP setup completed successfully. Keeping service alive...")
        
        # Keep the process running
        import signal
        import sys
        
        # Signal handler for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Received shutdown signal, exiting...")
            sys.exit(0)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep the container running
        try:
            while True:
                import time
                time.sleep(60)
                # Optionally check if RabbitMQ is still available
                if check_setup():
                    logger.info("Health check: RabbitMQ connection successful")
                else:
                    logger.warning("Health check: RabbitMQ connection failed")
        except KeyboardInterrupt:
            logger.info("Process interrupted")
    else:
        logger.error("AMQP setup failed")
        sys.exit(1)