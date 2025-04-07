import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

class Config:
    # Stripe settings
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')

    # Default URLs
    DEFAULT_SUCCESS_URL = os.getenv('DEFAULT_SUCCESS_URL', 'http://localhost:3000/success')
    DEFAULT_CANCEL_URL = os.getenv('DEFAULT_CANCEL_URL', 'http://localhost:3000/checkout?canceled=true')

    # RabbitMQ settings
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'amqp')  # Updated to use the Docker service name
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')

    # Queue names
    QUEUE_WEBHOOKS = os.getenv('QUEUE_WEBHOOKS', 'stripe_webhooks')
    QUEUE_NOTIFICATIONS = os.getenv('QUEUE_NOTIFICATIONS', 'stripe_notifications')

    # Feature flags
    ENABLE_ASYNC_REFUNDS = os.getenv('ENABLE_ASYNC_REFUNDS', 'True').lower() in ('true', '1', 't')
    RABBITMQ_REQUIRED = os.getenv('RABBITMQ_REQUIRED', 'False').lower() in ('true', '1', 't')

    # Connection retry parameters
    RABBITMQ_CONNECTION_ATTEMPTS = int(os.getenv('RABBITMQ_CONNECTION_ATTEMPTS', 3))
    RABBITMQ_CONNECTION_TIMEOUT = int(os.getenv('RABBITMQ_CONNECTION_TIMEOUT', 5))