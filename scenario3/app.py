# /Users/jonathanong/ByteMe/scenario3/requesting_refund.py

import requests
import json
from amqp_setup import publish_message
from config import Config

def get_order_details(order_id):
    response = requests.get(f"http://order-service/orders/{order_id}")
    return response.json()

def get_parts_in_order(order_id):
    response = requests.get(f"http://parts-service/orders/{order_id}/parts")
    return response.json()

def get_customer_details(customer_id):
    response = requests.get(f"http://customer-service/customers/{customer_id}")
    return response.json()

def create_delivery_task(delivery_data):
    publish_message(Config.QUEUE_DELIVERY_TASKS, delivery_data)

def initiate_refund(refund_data):
    publish_message(Config.QUEUE_REFUND_REQUESTS, refund_data)

def send_refund_email(email_data):
    publish_message(Config.QUEUE_EMAIL_REQUESTS, email_data)

def request_refund(order_id, customer_id):
    # Step 3: Get order details
    order_details = get_order_details(order_id)
    
    # Step 5: Get specific parts in order
    parts_details = get_parts_in_order(order_id)
    
    # Step 7: Get customer details
    customer_details = get_customer_details(customer_id)
    
    # Step 9: Create delivery task
    delivery_data = {
        "order_id": order_id,
        "customer_id": customer_id,
        "parts": parts_details,
        "delivery_address": customer_details["address"]
    }
    create_delivery_task(delivery_data)
    
    # Step 10: Initiate refund
    refund_data = {
        "payment_intent_id": order_details["payment_intent_id"],
        "amount": order_details["total_amount"],
        "customer_email": customer_details["email"],
        "order_id": order_id
    }
    initiate_refund(refund_data)
    
    # Step 11: Send refund email confirmation
    email_data = {
        "to_email": customer_details["email"],
        "subject": "Your refund request has been received",
        "content": f"Dear {customer_details['name']},\n\nWe have received your refund request for order {order_id}."
    }
    send_refund_email(email_data)
    
    # Step 12: Return refund confirmation
    return {
        "status": "success",
        "message": "Refund request has been initiated. You will receive an email confirmation shortly."
    }

# Example usage
if __name__ == "__main__":
    order_id = "12345"
    customer_id = "67890"
    result = request_refund(order_id, customer_id)
    print(result)