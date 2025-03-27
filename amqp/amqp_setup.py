import pika
import os
from os import environ

# Note about AMQP connection: various network firewalls, filters, gateways (e.g., SMU VPN on wifi), may hinder the connections;

# Connection settings
amqp_host = environ.get('rabbit_host') or 'localhost'
amqp_port = environ.get('rabbit_port') or 5672

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
    # For a BlockingConnection in AMQP clients,
    # when an exception happens when an action is performed,
    # it likely indicates a broken connection.
    # So, the code below actively calls a method in the 'connection' to check if an exception happens
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False

# Initialize exchanges and queues
def init_exchanges_and_queues():
    """Initialize all exchanges and their queues"""
    global connection, channel
    
    # Create/verify exchanges
    for exchange_name, exchange_type in EXCHANGES.items():
        channel.exchange_declare(
            exchange=exchange_name, 
            exchange_type=exchange_type, 
            durable=True
        )

    # Order-related queues
    create_queue(
        channel=channel,
        exchange_name="order_topic",
        queue_name="Order",
        routing_key="order.create"
    )
    
    create_queue(
        channel=channel,
        exchange_name="order_topic",
        queue_name="Delivery",
        routing_key="delivery.#"
    )
    
    create_queue(
        channel=channel,
        exchange_name="order_topic",
        queue_name="Parts",
        routing_key="parts.#"
    )

    # Notification queues
    create_queue(
        channel=channel,
        exchange_name="notification",
        queue_name="EmailNotifications",
        routing_key="notification.#"
    )

    # Payment/Refund queues
    create_queue(
        channel=channel,
        exchange_name="payment",
        queue_name="stripe_refund_requests",
        routing_key="refund.request"
    )
    
    create_queue(
        channel=channel,
        exchange_name="payment",
        queue_name="stripe_refund_responses",
        routing_key="refund.response"
    )

# Create initial connection
connection, channel = create_channel(
    hostname=amqp_host,
    port=amqp_port,
    exchange_name="order_topic",  # Default exchange
    exchange_type="topic"
)

# Initialize all exchanges and queues
init_exchanges_and_queues()