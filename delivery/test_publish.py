import pika
import json

# RabbitMQ connection details (use the same as in `amqp_setup.py`)
rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "order_topic"
routing_key = "delivery.task"  # Matches the wildcard "#" in your queue binding

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=rabbit_port))
channel = connection.channel()

# Publish a test message
message = {
    
    "order_id": "12345",
    "customer_id": "67890",
    "parts_list": ["part_1", "part_2"],
    "order_timestamp": "12/02/23"
}

channel.basic_publish(
    exchange=exchange_name,
    routing_key=routing_key,  # Should match a binding key in `amqp_setup.py`
    body=json.dumps(message),
    properties=pika.BasicProperties(    
        delivery_mode=2,  # Makes the message persistent
    )
)

print("✅ Test message sent to RabbitMQ!")
connection.close()
