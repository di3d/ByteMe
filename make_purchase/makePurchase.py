from flask import Flask, jsonify, request
from dotenv import load_dotenv
load_dotenv()
from dotenv import load_dotenv
load_dotenv()
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
partgetURL = environ.get("partgetURL")
partpostURL = environ.get("partpostURL")
partgetURL = environ.get("partgetURL")
partpostURL = environ.get("partpostURL")
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
    print("DEBUG recommendationURL:", recommendationURL)
    full_url = f"{recommendationURL}/{recommendation_id}"
    print("DEBUG FULL URL:", full_url)

    recommendation = invoke_http(full_url, method="GET")

    # recommendation = invoke_http(f"{recommendationURL}/{recommendation_id}", method="GET")
    print("DEBUG RECOMMENDATION RESPONSE:", recommendation)

    print("DEBUG recommendationURL:", recommendationURL)
    full_url = f"{recommendationURL}/{recommendation_id}"
    print("DEBUG FULL URL:", full_url)

    recommendation = invoke_http(full_url, method="GET")

    # recommendation = invoke_http(f"{recommendationURL}/{recommendation_id}", method="GET")
    print("DEBUG RECOMMENDATION RESPONSE:", recommendation)

    if recommendation.get("code") != 200:
        return jsonify (
            {
                "code":404,
                "message": "Recomendation not found"
            }
        ), 404
        
    parts_list = recommendation["data"]["parts_list"]
    available_parts = [] # get parts quantity to check for stock
    
    for parts in parts_list:
        part_id = parts["part_id"]
        part = invoke_http(f"{partgetURL}?ComponentId={part_id}", method="GET")
        if part.get("code") != 200:
            return jsonify (
                {
                    "code":404,
                    "message": "Part not found"
                }
            ), 404
            
        stock = part["data"]["Stock"] #boolen option; stock available or no?
        stock = part["data"]["Stock"] #boolen option; stock available or no?
        
        if stock>0:
        if stock>0:
            available_parts.append(
                {
                    "Id":part_id,
                    "Name":part["data"]["Name"],
                    "Price":part["data"]["Price"],
                    "Stock":part["data"]["Stock"],
                    "ImageUrl":part["data"]["ImageUrl"],
                    "CreatedAt":part["data"]["CreatedAt"],
                    "CategoryId":part["data"]["CategoryId"],
                    "Id":part_id,
                    "Name":part["data"]["Name"],
                    "Price":part["data"]["Price"],
                    "Stock":part["data"]["Stock"],
                    "ImageUrl":part["data"]["ImageUrl"],
                    "CreatedAt":part["data"]["CreatedAt"],
                    "CategoryId":part["data"]["CategoryId"],
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
        total_price += part["Price"]
        
        total_price += part["Price"]
        
    payment_payload = {
        "customer_id": customer_id,
        "amount": total_price,
        "customer_email": customer_details["email"],
        "product_name": "Purchase from ByteMe",
        "success_url": "http://localhost:3000/success",  # 👈 Adjust as needed
        "cancel_url": "http://localhost:3000/cancel",    # 👈 Adjust as needed
        "metadata": {
            "customer_id": customer_id
        }
    }
    
    payment_response = invoke_http(f"{stripeURL}/create-checkout-session", method="POST", json=payment_payload)
        "customer_email": customer_details["email"],
        "product_name": "Purchase from ByteMe",
        "success_url": "http://localhost:3000/success",  # 👈 Adjust as needed
        "cancel_url": "http://localhost:3000/cancel",    # 👈 Adjust as needed
        "metadata": {
            "customer_id": customer_id
        }
    }
    
    payment_response = invoke_http(f"{stripeURL}/create-checkout-session", method="POST", json=payment_payload)
    
    if payment_response.get("code") != 200:
        return jsonify(
            {
                "code": 402, 
                "message": "Payment failed", 
                "details": payment_response
            }
        ), 402
        
    order_id = payment_response["data"]["payment_intent_id"]
    checkout_url = payment_response["data"]["checkout_url"]
        
    order_id = payment_response["data"]["payment_intent_id"]
    checkout_url = payment_response["data"]["checkout_url"]
        
    #6. place order via amqp
    timestamp = datetime.now().isoformat()
    order_data = {
        "order_id": order_id,
        "customer_id": customer_id,
        "parts_list": parts_list,
        "timestamp": timestamp,
        "status": "confirmed" 
    }

    order_response = invoke_http(f"{environ.get('orderURL')}/order", method="POST", json=order_data)
    
    order_response = invoke_http(f"{environ.get('orderURL')}/order", method="POST", json=order_data)
    
    
    # 7. Update parts stock count via AMQP
    # for part in available_parts:
    #     new_qty = part["Stock"]-1
    #     part_data = {
    #         "Id": part["part_id"],
    #         "Name":part["data"]["Name"],
    #         "Price":part["data"]["Price"],
    #         "Stock": max(0, new_qty),
    #         "ImageUrl":part["ImageUrl"],
    #         "CreatedAt":part["CreatedAt"],
    #         "CategoryId": part["CategoryId"],
    #     }
    # for part in available_parts:
    #     new_qty = part["Stock"]-1
    #     part_data = {
    #         "Id": part["part_id"],
    #         "Name":part["data"]["Name"],
    #         "Price":part["data"]["Price"],
    #         "Stock": max(0, new_qty),
    #         "ImageUrl":part["ImageUrl"],
    #         "CreatedAt":part["CreatedAt"],
    #         "CategoryId": part["CategoryId"],
    #     }
        
    #     invoke_http(f"{partpostURL}/{part['part_id']}", method="PUT", json=part_data)
    #     invoke_http(f"{partpostURL}/{part['part_id']}", method="PUT", json=part_data)
        
        
    #8. send delivery task to delivery queue via amqp
    delivery_data = {
        "order_id":order_id,
        "customer_id":customer_id,
        "parts_list":available_parts
    }
    
    delivery_response = invoke_http(f"{deliveryURL}/delivery", method="POST", json=delivery_data)
    
    if delivery_response.get("code") != 201:
        return jsonify({"code": 500, "message": "Failed to create delivery"}), 500
    
    
    # Return final confirmation
    return jsonify({
        "code": 200,
        "message": "Purchase completed successfully",
        "data": {
            "order_id": order_id,
            "checkout": payment_response.get("data", {})  # you can tweak this
        }
    }), 200
    delivery_response = invoke_http(f"{deliveryURL}/delivery", method="POST", json=delivery_data)
    
    if delivery_response.get("code") != 201:
        return jsonify({"code": 500, "message": "Failed to create delivery"}), 500
    
    
    # Return final confirmation
    return jsonify({
        "code": 200,
        "message": "Purchase completed successfully",
        "data": {
            "order_id": order_id,
            "checkout": payment_response.get("data", {})  # you can tweak this
        }
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5008, debug=True)    


