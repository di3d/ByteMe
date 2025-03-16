import pika
import json

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Test order data
order_data = {
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "parts_list": ["CPU", "RAM", "SSD"]
}

# Publish order to "Order" queue
channel.basic_publish(
    exchange="order_topic",
    routing_key="order.create",
    body=json.dumps(order_data)
)

print("✅ Test Order Sent")
connection.close()
