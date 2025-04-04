import os


class Config:
    # RabbitMQ settings matching docker-compose port mappings
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', '5673'))
    RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD', 'guest')
    
    # Additional RabbitMQ settings required by amqp_setup.py
    RABBITMQ_EXCHANGE = ""
    RABBITMQ_QUEUE = "refund_queue"
    RABBITMQ_ROUTING_KEY = "refund.request"