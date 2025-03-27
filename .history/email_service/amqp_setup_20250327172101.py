from email_service.config import EmailConfig
import pika

# Use the configuration from EmailConfig
connection = EmailConfig.get_rabbitmq_connection()
channel = connection.channel()

def check_setup():
    """Check and setup RabbitMQ connection and channel"""
    global connection, channel
    
    if connection.is_closed:
        connection = EmailConfig.get_rabbitmq_connection()
    
    if channel.is_closed:
        channel = connection.channel()
    
    return channel