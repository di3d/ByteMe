import pika
import os
from os import environ

# Note about AMQP connection: various network firewalls, filters, gateways (e.g., SMU VPN on wifi), may hinder the connections;
# If "pika.exceptions.AMQPConnectionError" happens, may try again after disconnecting the wifi and/or disabling firewalls.
# If see: Stream connection lost: ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None)
# - Try: simply re-run the program or refresh the page.
# For rare cases, it's incompatibility between RabbitMQ and the machine running it,
# - Use the Docker version of RabbitMQ instead: https://www.rabbitmq.com/download.html

"""
variables for creating a connection with AMQP server
"""


# Detect if running inside Docker
RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"

# Set RabbitMQ Configuration Dynamically
if RUNNING_IN_DOCKER:
    amqp_host = "amqp"  # Use the RabbitMQ service name in Docker Compose
    amqp_port = 5672    # Default RabbitMQ port inside Docker
else:
    amqp_host = "localhost"  # Local environment
    amqp_port = 5672         # RabbitMQ port on the host machine
    

exchange_name = "order_topic"
exchange_type = "topic"

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
    
def publish_message(exchange_name, routing_key, message):
    try:
        connection, channel = create_channel()
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )
        print(f"Message published to exchange '{exchange_name}' with routing key '{routing_key}': {message}")
        connection.close()
    except Exception as e:
        print(f"Failed to publish message: {e}")

setup_rabbitmq()