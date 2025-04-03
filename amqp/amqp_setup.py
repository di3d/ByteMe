# unified_amqp_setup.py
import pika
import os
from os import environ
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../stripe')))
from amqp.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection settings
# Force RabbitMQ to use IPv4 explicitly
amqp_host = '127.0.0.1'  # Override any other configuration to ensure IPv4 usage
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
def create_channel():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=amqp_host,
            port=amqp_port,
            heartbeat=3600,
            blocked_connection_timeout=3600,  # these parameters to prolong the expiration time (in seconds) of the connection
        ))

    channel = connection.channel()  # connection to the AMQP server is created
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)  # 'durable' makes the exchange survive broker restarts

    return connection, channel

"""
function to create the required queues
"""
def create_queue(channel, exchange_name, queue_name, routing_key):
    print(f"Bind to queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)  # 'durable' makes the queue survive broker restarts
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)  # bind the queue to the exchange via the routing_key

def setup_rabbitmq():
    connection, channel = create_channel()
    create_queue(channel, exchange_name, "Order", "order.create")
    create_queue(channel, exchange_name, "Delivery", "delivery.#")
    create_queue(channel, exchange_name, "Parts", "parts.#")

"""
This function in this module sets up a connection and a channel to a local AMQP broker,
and declares a 'topic' exchange to be used by the microservices in the solution.
"""
def check_setup():
    # The shared connection and channel created when the module is imported may be expired,
    # timed out, disconnected by the broker or a client;
    # - re-establish the connection/channel is they have been closed
    global connection, channel, amqp_host, amqp_port, exchange_name, exchange_type

    if not is_connection_open(connection):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=amqp_host,
                port=amqp_port,
                heartbeat=3600,
                blocked_connection_timeout=3600))  # re

    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)

def is_connection_open(connection):
    """Check if a connection is still open"""
    try:
        if connection is None:
            return False
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        logger.error(f"AMQP Error: {str(e)}")
        logger.info("Creating a new connection...")
        return False

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