import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

class EmailConfig:
    """Email service configuration"""
    # SendGrid settings
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    
    # Email sender settings
    EMAIL_FROM_ADDRESS = os.getenv('SENDGRID_SENDER_EMAIL', 'noreply@byteme.store')
    EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'ByteMe Store')
    
    # Email templates
    TEMPLATE_REFUND_INITIATED = os.getenv('TEMPLATE_REFUND_INITIATED')
    TEMPLATE_REFUND_PROCESSED = os.getenv('TEMPLATE_REFUND_PROCESSED')
    TEMPLATE_REFUND_FAILED = os.getenv('TEMPLATE_REFUND_FAILED')
    
    # Service configuration
    DEBUG_MODE = os.getenv('EMAIL_DEBUG', 'False').lower() in ('true', '1', 't')
    QUEUE_EMAIL_REQUESTS = os.getenv('QUEUE_EMAIL_REQUESTS', 'email_requests')
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')  # Note the quotes around 'localhost'
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))  # Use string '5672'
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
    
    @classmethod
    def get_rabbitmq_connection(cls):
        """
        Establish and return a RabbitMQ connection
        
        Returns:
            pika.BlockingConnection: A RabbitMQ connection
        """
        try:
            # Connection parameters
            credentials = pika.PlainCredentials(cls.RABBITMQ_USER, cls.RABBITMQ_PASS)
            parameters = pika.ConnectionParameters(
                host=cls.RABBITMQ_HOST, 
                port=cls.RABBITMQ_PORT, 
                credentials=credentials
            )
            
            # Create connection
            connection = pika.BlockingConnection(parameters)
            return connection
        except Exception as e:
            print(f"Error establishing RabbitMQ connection: {e}")
            raise

    @classmethod
    def check_rabbitmq_setup(cls):
        """
        Check RabbitMQ connection and create a channel
        
        Returns:
            pika.adapters.blocking_connection.BlockingChannel: A RabbitMQ channel
        """
        try:
            connection = cls.get_rabbitmq_connection()
            channel = connection.channel()
            return channel
        except Exception as e:
            print(f"Error setting up RabbitMQ: {e}")
            raise