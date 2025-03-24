from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from invokes import invoke_http
import pika
from datetime import datetime
import uuid
import sys
from os import environ
import json
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
CORS(app)

# RabbitMQ connection details (use the same as in `amqp_setup.py`)
rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "order_topic"

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=rabbit_port))
channel = connection.channel()

# Relevant REST APIs (microservices)
customerURL = environ.get('customerURL')
recommendationURL = environ.get("recommendationURL")
partURL = environ.get("partURL")
deliveryURL = environ.get("deliveryURL")
stripeURL = environ.get("stripeURL")


def send_amqp_message(exchange_name, routing_key, message):
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,  # Should match a binding key in `amqp_setup.py`
        body=json.dumps(message),
        properties=pika.BasicProperties(    
            delivery_mode=2,  # Makes the message persistent
        )
    )
    

@app.route("/purchase", methods=['POST'])
def make_purchase():
    
    #1. validation of request passed through post
    data = request.get_json() #extact json data passed in when user creates an account
    
    required_fields = ["recommendation_id", "customer_id"]
    for field in required_fields:
        if field not in data:
            return jsonify(
                {
                    "code": 400, 
                    "message": f"Missing required field: {field}"
                }
            ), 400
            
    recommendation_id = data["recommendation_id"]
    customer_id = data["customer_id"]
    
    #2. get recommendation details (parts list) GET request
    recommendation = invoke_http(f"{recommendationURL}/{recommendation_id}", method="GET")
    if recommendation.get("code") != 200:
        return jsonify (
            {
                "code":404,
                "message": "Reccomendation not found"
            }
        ), 404
        
    parts_list = recommendation["data"]["parts_list"]
    available_parts = [] # get parts quantity to check for stock
    
    for parts in parts_list:
        part_id = parts["part_id"]
        part = invoke_http(f"{partURL}/{part_id}", method="GET")
        if part.get("code") != 200:
            return jsonify (
                {
                    "code":404,
                    "message": "Part not found"
                }
            ), 404
            
        stock = part["data"]["available"] #boolen option; stock available or no?
        
        if stock:
            available_parts.append(
                {
                    "part_id":part_id,
                    "price":part["data"]["price"],
                    "qunatity":part["data"]["quantity"],
                    "availability":part["data"]["availability"],
                    "description":part["data"]["description"]
                }
            )
            
    #3. get customer entirety of customer details (GET request)
    customer = invoke_http(f"{customerURL}/{customer_id}", method="GET")
    if customer.get("code") != 200:
        return jsonify (
            {
                "code":404,
                "message": "Reccomendation not found"
            }
        ), 404
        
    customer_details = customer["data"]
    
    #5. initiate payment via stripe
    total_price = 0
    for part in available_parts:
        total_price += part["price"]
    payment_payload = {
        "customer_id": customer_id,
        "amount": total_price,
        "email": customer_details["email"]
    }
    payment_response = invoke_http(stripeURL, method="POST", json=payment_payload)
    
    if payment_response.get("code") != 200:
        return jsonify(
            {
                "code": 402, 
                "message": "Payment failed", 
                "details": payment_response
            }
        ), 402
        
    #6. place order via amqp
    order_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    order_data = {
        "order_id": order_id,
        "customer_id": customer_id,
        "parts_list": parts_list,
        "timestamp": timestamp,
        "status": "confirmed" 
    }

    send_amqp_message(exchange_name, "order.create", order_data)
    
    # 7. Update parts stock count via AMQP
    for part in available_parts:
        new_qty = part["quantity"]-1
        part_data = {
            "part_id": part["part_id"],
            "description": part["descirption"],
            "quantity": max(0, new_qty),
            "available": new_qty > 0
        }
        
        send_amqp_message(exchange_name, "parts.task", part_data)
        
        
    #8. send delivery task to delivery queue via amqp

    delivery_data = {
        "order_id":order_id,
        "customer_id":customer_id,
        "parts_list":available_parts
    }
    
    send_amqp_message(exchange_name, "delivery.task", delivery_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5008, debug=True)    


