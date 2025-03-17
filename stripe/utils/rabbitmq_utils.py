import pika
import json
import time
import socket
from config import Config

def get_rabbitmq_connection():
    """
    Create a new connection to RabbitMQ.
    
    Returns:
        pika.BlockingConnection: An established connection or None if failed
    """
    try:
        credentials = pika.PlainCredentials(
            Config.RABBITMQ_USER, 
            Config.RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=Config.RABBITMQ_HOST,
            port=Config.RABBITMQ_PORT,
            credentials=credentials,
            connection_attempts=1,  # Fast fail if RabbitMQ is not available
            socket_timeout=2,  # Timeout after 2 seconds
            blocked_connection_timeout=2  # Additional timeout parameter
        )
        return pika.BlockingConnection(parameters)
    except pika.exceptions.AMQPConnectionError as e:
        print(f"RabbitMQ connection error: Could not connect to RabbitMQ at {Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}")
        print(f"Detailed error: {str(e)}")
        return None
    except socket.gaierror as e:
        print(f"RabbitMQ DNS resolution error: {str(e)}")
        return None
    except Exception as e:
        print(f"RabbitMQ connection error: {str(e)}")
        return None

def setup_rabbitmq():
    """
    Set up RabbitMQ queues.
    
    Returns:
        bool: True if setup was successful, False otherwise
    """
    try:
        connection = get_rabbitmq_connection()
        if not connection:
            return False
            
        channel = connection.channel()
        
        # Declare queues
        channel.queue_declare(queue=Config.QUEUE_REFUND_REQUESTS, durable=True)
        channel.queue_declare(queue=Config.QUEUE_REFUND_RESPONSES, durable=True)
        channel.queue_declare(queue=Config.QUEUE_WEBHOOKS, durable=True)
        
        connection.close()
        print("RabbitMQ queues initialized")
        return True
    except Exception as e:
        print(f"Error setting up RabbitMQ: {str(e)}")
        return False

def publish_message(queue_name, message):
    """
    Publish a message to a RabbitMQ queue.
    
    Args:
        queue_name (str): The name of the queue
        message (dict): The message to publish
        
    Returns:
        bool: True if the message was published, False otherwise
    """
    try:
        connection = get_rabbitmq_connection()
        if not connection:
            return False
            
        channel = connection.channel()
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json',
                correlation_id=message.get('correlation_id', ''),
                message_id=str(time.time())
            )
        )
        
        connection.close()
        return True
    except Exception as e:
        print(f"RabbitMQ publish error: {str(e)}")
        return False