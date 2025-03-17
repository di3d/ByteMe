import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Stripe settings
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    # Default URLs
    DEFAULT_SUCCESS_URL = os.getenv('DEFAULT_SUCCESS_URL', 'http://localhost:3000/success')
    DEFAULT_CANCEL_URL = os.getenv('DEFAULT_CANCEL_URL', 'http://localhost:3000/checkout?canceled=true')
    
    # RabbitMQ settings
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    
    # Queue names
    QUEUE_REFUND_REQUESTS = os.getenv('QUEUE_REFUND_REQUESTS', 'stripe_refund_requests')
    QUEUE_REFUND_RESPONSES = os.getenv('QUEUE_REFUND_RESPONSES', 'stripe_refund_responses')
    QUEUE_WEBHOOKS = os.getenv('QUEUE_WEBHOOKS', 'stripe_webhooks')
    
    # Feature flags
    ENABLE_ASYNC_REFUNDS = os.getenv('ENABLE_ASYNC_REFUNDS', 'True').lower() in ('true', '1', 't')
    RABBITMQ_REQUIRED = os.getenv('RABBITMQ_REQUIRED', 'False').lower() in ('true', '1', 't')
    
    # Connection retry parameters
    RABBITMQ_CONNECTION_ATTEMPTS = int(os.getenv('RABBITMQ_CONNECTION_ATTEMPTS', 1))
    RABBITMQ_CONNECTION_TIMEOUT = int(os.getenv('RABBITMQ_CONNECTION_TIMEOUT', 2))