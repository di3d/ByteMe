import pika
import json

# RabbitMQ connection details (use the same as in `amqp_setup.py`)
rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "order_topic"
routing_key = "order.create"

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=rabbit_port))
channel = connection.channel()

# Test order data
order_data = {
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "parts_list": ["CPU", "RAM", "SSD"]
}

# Publish order to "Order" queue
channel.basic_publish(
    exchange=exchange_name,
    routing_key=routing_key,
    body=json.dumps(order_data),
    properties=pika.BasicProperties(
        delivery_mode=2,  # Makes the message persistent
    )
)

print("✅ Test Order Sent")
connection.close()
