from flask import Flask, jsonify, request
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
import requests
from os import environ
import json


app = Flask(__name__)
CORS(app)

# RabbitMQ connection details (use the same as in `amqp_setup.py`)
rabbit_host = "localhost"
rabbit_port = 5673
exchange_name = "order_topic"

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=rabbit_port))
channel = connection.channel()

# Set default values for environment variables
environ.setdefault("customerURL", "http://localhost:5001/customer")
environ.setdefault("recommendationURL", "http://localhost:5009/cart")
environ.setdefault("partpostURL", "https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/AddComponent")
environ.setdefault("partgetURL", "https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/GetComponentById")
environ.setdefault("orderURL", "http://localhost:5002/")
environ.setdefault("deliveryURL", "http://localhost:5003/")
environ.setdefault("stripeURL", "http://localhost:5000/")


# Relevant REST APIs (microservices)
customerURL = environ.get('customerURL')
recommendationURL = environ.get("recommendationURL")
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


@app.route("/initial_purchase", methods=['POST'])
def make_purchase():
    
    """
    1. Validation of passed request through POST
    """
    # - using request.get_json(); users need to pass in 2 vairables
    # - recommendation_id and customer_id
    data = request.get_json()
    print(data)
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


    """
    2. get recommendation details (parts list) GET request
    """
    # - first get the specific recommendaion using the recommendation id
    # - second get the parts list from the recommendation 
    # - get the parts id from parts list and get the stock count using parts id
    # - only proceed if stock count for the item is > 0
    print("DEBUG recommendationURL:", recommendationURL)
    full_url = f"{recommendationURL}/{recommendation_id}"
    print("DEBUG FULL URL:", full_url)
    print("DEBUG ENV recommendationURL:", recommendationURL)


    recommendation = invoke_http(full_url, method="GET")

    if recommendation.get("code") != 200:
        return jsonify (
            {
                "code":404,
                "message": "Recommendation not found"
            }
        ), 404
        
    parts_list = recommendation["data"]["parts_list"]
    available_parts = [] # get parts quantity to check for stock    
    for parts in parts_list:
        part_id = int(parts)

        try:
            # Construct the full API URL
            api_url = f"https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/GetComponentById?ComponentId={part_id}"
            response = requests.get(api_url)   # Make the GET request to OutSystems API
            response.raise_for_status()   # Check if the request was successful
            part = response.json()
            
            # Print to console
            print("API Response:")
            print(json.dumps(part, indent=2))

            stock = part["Stock"]
                
            if stock>0:
                available_parts.append(
                    {
                        "Id":part_id,
                        "Name":part["Name"],
                        "Price":part["Price"],
                        "Stock":part["Stock"],
                        "ImageUrl":part["ImageUrl"],
                        "CreatedAt": part.get("CreatedAt", ""),  # fallback if missing
                        "CategoryId":part["CategoryId"],
                    }
                )

        except requests.exceptions.RequestException as e:
            print(f"Error calling OutSystems API: {str(e)}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500


    """
    3. get customer entirety of customer details (GET request)
    """
    # - retrieve customer details to get their email to be stored in the delivery microservice
    customer = invoke_http(f"{customerURL}/{customer_id}", method="GET")
    if customer.get("code") != 200:
        return jsonify (
            {
                "code":404,
                "message": "Recommendation not found"
            }
        ), 404
        
    customer_details = customer["data"]


    """
    4. initiate payment via stripe
    """
    # - send the payload to stripe with the required details amount, currency and email
    # - stripe will return the session id; using the session id, retrieve the payement intent id
    # - from the initial response from create-checkout-session, retrieve the checkout url
    total_price = 0

    for part in available_parts:
        total_price += part["Price"]
        
    total_price = int(total_price * 100)
    payment_payload = {
        "amount": total_price,
        "currency": "sgd",
        "customer_email": customer_details["email"],   
    }
    
    payment_response = invoke_http(f"{stripeURL}/create-checkout-session", method="POST", json=payment_payload)
    
    if "url" not in payment_response:
        return jsonify(
            {
                "code": 402, 
                "message": "Payment failed", 
                "details": payment_response
            }
        ), 402
        
    session_id = payment_response["data"]["session_id"] # retrieve the session id from the response
    checkout_url = payment_response["data"]["checkout_url"] # retrieve the checkout url from the PAYMENT response

    checkout_details = {
        "session_id": session_id,
        "checkout_url": checkout_url,
        "customer_id": customer_id,
        "parts_list": available_parts
    }

    return jsonify(
        {
            "code": 200,
            "message": "Checkout session created",
            "data": checkout_details
        }
    ), 200


@app.route("/final_purchase", methods=['POST'])
def make_purchase_after_stripe():

    """
    5. Placing an order using HTTP POST
    """
    # - use the stipe payment intend id as the order id;

    data = request.get_json()
    
    required_fields = ["session_id", "customer_id", "parts_list"]
    for field in required_fields:
        if field not in data:
            return jsonify(
                {
                    "code": 405, 
                    "message": f"Missing required field: {field}"
                }
            ), 400
    
    session_id = data["session_id"]
    customer_id = data["customer_id"]
    parts_list = data["parts_list"]
    
    checkout_response = invoke_http(f"{stripeURL}/checkout-session?session_id={session_id}", method="GET")
    if checkout_response.get("payment_intent") is None:
        return jsonify(
            {
                "code": 402, 
                "message": "Payment failed", 
                "details": checkout_response
            }
        ), 402

    order_id = checkout_response["payment_intent"] # retrieve the payment intent id from the CHECKOUT response

    order_data = {
        "order_id": order_id,
        "customer_id": customer_id,
        "parts_list": parts_list,
    }
    order_response = invoke_http(f"{environ.get('orderURL')}/order", method="POST", json=order_data)

    if order_response.get("code") != 201:
        return jsonify({"code": 500, "message": "Failed to create order"}), 500
    
    
    """
    6. update the parts stock count
    """
    for part in parts_list:
        new_qty = part["Stock"]-1
        part_data = {
            "Id": part["Id"],
            "Name":part["Name"],
            "Price":part["Price"],
            "Stock": max(0, new_qty),
            "ImageUrl":part["ImageUrl"],
            "CreatedAt":part["CreatedAt"],
            "CategoryId": part["CategoryId"],
        }

        try:
            api_url = f"https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/UpdateComponent"
            response = requests.put(api_url, json=part_data)   # Make the PUT request to OutSystems API
            response.raise_for_status()   # Check if the request was successful
            print(f"Successfully updated stock for part ID {part['Id']}")



        except requests.exceptions.RequestException as e:
            print(f"Failed to update part ID {part['Id']}: {str(e)}")

        
    """
    7. send delivery task using http POST
    """
    # - use the stipe payment intend id as the order id
    # - use the customer email to send the delivery details
    delivery_data = {
        "order_id":order_id,
        "customer_id":customer_id
    }
    
    delivery_response = invoke_http(f"{deliveryURL}/delivery", method="POST", json=delivery_data)
    
    if delivery_response.get("code") != 201:
        return jsonify({"code": 500, "message": "Failed to create delivery"}), 500
    
    
    # Return final confirmation
    return jsonify({
        "code": 200,
        "message": "Purchase completed successfully",
        "data": {
            "order_id": order_id
        }            
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5008, debug=True)    


