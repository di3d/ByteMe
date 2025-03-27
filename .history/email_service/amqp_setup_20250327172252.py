import pika
from email_service.config import EmailConfig
import logging

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
        
        logger.info("RabbitMQ connection established successfully")
        return connection, channel
    except Exception as e:
        logger.error(f"Error establishing RabbitMQ connection: {e}")
        raise

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