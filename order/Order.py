from flask import Flask, jsonify
from flask_cors import CORS
import firebase_admin
import pika
import uuid
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../amqp')))
import amqp_setup
import json
from firebase_admin import credentials, db


app = Flask(__name__)
CORS(app)

rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "order_topic"
exchange_type = "topic"


# Fetch the service account key JSON file contents
cred = credentials.Certificate('./../privateKey.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://esdteam3g7-73a7b-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('Orders')

"""
function to strcture the delivery log in json format to store in rtdb
"""
def store_order_to_db(data):
    # Generate a unique order_id
    order_id = str(uuid.uuid4())
    order_date = datetime.utcnow().isoformat()
    
    #structure the received data in json format to store to rtdb
    order_data = {
        "customer_id": data["customer_id"],
        "parts_list": data.get("parts_list", "N/A"),
        "timestamp": order_date,
        "status": "pending" 
    }
    ref.child(order_id).set(order_data)
    

"""
callback function to process the message from the queue
"""
def callback(channel, method, properties, body):
    # processes incoming orders and stores them in rtdb
    try:
        data = json.loads(body)
        store_order_to_db(data)
        channel.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message
        print("Update to firebase successful")
        
    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"Error message: {body}")
    print()
    

"""
starts this microservice to listen to the queue for any incoming messags
"""    
def start_consumer():
    amqp_setup.check_setup()
    
    # Use the existing channel from amqp_setup
    channel = amqp_setup.channel 
    
    queue_name = "Delivery"
    
    # Start consuming messages from the delivery queue
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    
    print(f"Delivery Microservice listening on queue: {queue_name}")
    channel.start_consuming()
        
    
if __name__ == '__main__':
    try:
        start_consumer()
    
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
    
    
