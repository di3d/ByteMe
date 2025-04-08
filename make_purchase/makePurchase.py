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

# Set default values for environment variables
environ.setdefault("customerURL", "http://customer:5001/customer")
environ.setdefault("recommendationURL", "http://cart:5009/cart")
environ.setdefault("partpostURL", "https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/AddComponent")
environ.setdefault("partgetURL", "https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/GetComponentById")
environ.setdefault("orderURL", "http://order:5002/")
environ.setdefault("deliveryURL", "http://delivery:5003/")
environ.setdefault("stripeURL", "http://stripe:5000/")


# Relevant REST APIs (microservices)
customerURL = environ.get('customerURL')
recommendationURL = environ.get("recommendationURL")
partgetURL = environ.get("partgetURL")
partpostURL = environ.get("partpostURL")
deliveryURL = environ.get("deliveryURL")
stripeURL = environ.get("stripeURL")

# In-memory session storage (in production, you'd use a database)
session_store = {}


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

    print(recommendation)
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
                "message": "Customer not found"
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

    # Store the session data for later retrieval
    # Extract just the relevant IDs from parts to make the data smaller
    part_ids = [part["Id"] for part in available_parts]
    session_store[session_id] = {
        "customer_id": customer_id,
        "parts_list": part_ids,
        "parts_details": available_parts,  # Keep full details for later use
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"Stored session data for {session_id}: {json.dumps(session_store[session_id], default=str)}")

    checkout_details = {
        "session_id": session_id,
        "checkout_url": checkout_url,
    }

    return jsonify(
        {
            "code": 200,
            "message": "Checkout session created",
            "data": checkout_details
        }
    ), 200


@app.route("/get_session_data/<session_id>", methods=['GET'])
def get_session_data(session_id):
    """Get stored session data by session ID"""
    if session_id in session_store:
        return jsonify({
            "code": 200,
            "data": session_store[session_id]
        })
    else:
        return jsonify({
            "code": 404,
            "message": "Session not found"
        }), 404


@app.route("/final_purchase", methods=['POST'])
def make_purchase_after_stripe():
    data = request.get_json()
    print("Received data:", data)
    
    # Check for either session_id or payment_intent
    session_id = data.get("session_id")
    payment_intent_id = data.get("payment_intent")
    
    # Must have at least one of these
    if not (session_id or payment_intent_id):
        return jsonify({"code": 405, "message": "Missing required field: session_id or payment_intent"}), 400
    
    # Try to get customer_id and parts_list from session store if not provided
    if session_id and session_id in session_store:
        session_data = session_store[session_id]
        customer_id = data.get("customer_id", session_data["customer_id"])
        parts_list = data.get("parts_list", session_data["parts_list"])
        parts_details = session_data.get("parts_details", [])
        print(f"Retrieved session data for {session_id}: customer_id={customer_id}, parts_list={parts_list}")
    else:
        # Check if both customer_id and parts_list are provided in the request
        if not data.get("customer_id") or not data.get("parts_list"):
            return jsonify({"code": 405, "message": "Missing required field: customer_id or parts_list"}), 400
        customer_id = data.get("customer_id")
        parts_list = data.get("parts_list")
        parts_details = []  # Will need to fetch these
    
    # If we have session_id, get payment_intent from it
    order_id = None
    if session_id:
        print(f"Getting payment intent from session ID: {session_id}")
        checkout_response = invoke_http(f"{stripeURL}/checkout-session?session_id={session_id}", method="GET")
        print("Checkout response:", checkout_response)
        
        if checkout_response.get("payment_intent") is None:
            return jsonify({"code": 402, "message": "Payment failed", "details": checkout_response}), 402
        order_id = checkout_response["payment_intent"]
    else:
        # Use the provided payment_intent directly
        order_id = payment_intent_id
    
    print(f"Using order ID: {order_id}")
    print(f"Using customer ID: {customer_id}")
    print(f"Using parts list: {parts_list}")

    # Create the order
    order_data = {
        "order_id": order_id,
        "customer_id": customer_id,
        "parts_list": parts_list,
    }
    
    print(f"Sending order data to order service: {order_data}")
    order_response = invoke_http(f"{environ.get('orderURL')}/order", method="POST", json=order_data)
    print(f"Order service response: {order_response}")

    if order_response.get("code") != 201:
        return jsonify({"code": 500, "message": f"Failed to create order: {order_response}"}), 500
    
    # Prepare parts details for stock update
    # If we already have parts_details from the session, use them
    # Otherwise, fetch the details for each part ID
    if not parts_details:
        parts_details = []
        for part_id in parts_list:
            try:
                api_url = f"https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/GetComponentById?ComponentId={part_id}"
                response = requests.get(api_url)
                response.raise_for_status()
                part = response.json()
                parts_details.append(part)
            except requests.exceptions.RequestException as e:
                print(f"Error retrieving part {part_id}: {str(e)}")
                # Continue with the next part, don't fail the whole order
    
    """
    6. update the parts stock count
    """
    for part in parts_details:
        new_qty = part["Stock"]-1
        part_data = {
            "Id": part["Id"],
            "Name":part["Name"],
            "Price":part["Price"],
            "Stock": max(0, new_qty),
            "ImageUrl":part["ImageUrl"],
            "CreatedAt": part.get("CreatedAt", ""),
            "CategoryId": part["CategoryId"],
        }

        try:
            api_url = f"https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/UpdateComponent"
            response = requests.put(api_url, json=part_data)
            response.raise_for_status()
            print(f"Successfully updated stock for part ID {part['Id']}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to update part ID {part['Id']}: {str(e)}")
            # Continue with the next part, don't fail the whole order
        
    """
    7. send delivery task using http POST
    """
    # - use the stipe payment intend id as the order id
    # - use the customer email to send the delivery details
    delivery_data = {
        "order_id":order_id,
        "customer_id":customer_id
    }
    
    print(f"Sending delivery data: {delivery_data}")
    delivery_response = invoke_http(f"{deliveryURL}/delivery", method="POST", json=delivery_data)
    print(f"Delivery response: {delivery_response}")
    
    if delivery_response.get("code") != 201:
        return jsonify({"code": 500, "message": f"Failed to create delivery: {delivery_response}"}), 500
    
    # Clean up the session data now that order is complete
    if session_id in session_store:
        del session_store[session_id]
        print(f"Removed session data for {session_id}")
    
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