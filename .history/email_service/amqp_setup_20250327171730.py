import pika
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')

# Connection parameters
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)

# Expose the connection object
connection = pika.BlockingConnection(parameters)

# Channel setup
channel = connection.channel()

def check_setup():
    """Check and setup RabbitMQ connection and channel"""
    global connection, channel
    if connection.is_closed:
        connection = pika.BlockingConnection(parameters)
    if channel.is_closed:
        channel = connection.channel()
    return channel