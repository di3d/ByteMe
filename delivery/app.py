from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pika
import uuid
from datetime import datetime
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../amqp')))

# Check if we should skip AMQP setup
if not os.getenv('SKIP_AMQP_SETUP'):
    import amqp_setup

app = Flask(__name__)
CORS(app)

# Detect if running inside Docker
RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"

# Set Database Configuration Dynamically
if RUNNING_IN_DOCKER:
    DB_HOST = "postgres"  # Docker network name
    DB_PORT = "5432"

else:
    DB_HOST = "localhost"  # Local environment
    DB_PORT = "5432"

DB_PORT = "5432"
DB_NAME = os.getenv("DB_NAME", "delivery_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "iloveESD123")

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the Delivery model
class Delivery(db.Model):
    id = db.Column(db.String, primary_key=True)
    order_id = db.Column(db.String, nullable=False)
    customer_id = db.Column(db.String, nullable=False)
    parts_list = db.Column(db.Text, nullable=False)  # Store as JSON string
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route("/delivery/<string:delivery_id>", methods=['GET'])
def get_delivery(delivery_id):
    # Retrieve delivery from PostgreSQL
    delivery = Delivery.query.get(delivery_id)
    if delivery:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "delivery_id": delivery.id,
                    "order_id": delivery.order_id,
                    "customer_id": delivery.customer_id,
                    "parts_list": json.loads(delivery.parts_list),  # Deserialize JSON string
                    "timestamp": delivery.timestamp.isoformat()
                }
            }
        ), 200
    else:
        return jsonify(
            {
                "code": 404,
                "message": "Delivery not found"
            }
        ), 404

@app.route("/delivery", methods=['POST'])
def create_delivery():
    try:
        data = request.get_json()  # Extract JSON data passed in when user creates a delivery
        
        # Validate fields to be passed on to delivery JSON format
        required_fields = ["order_id", "customer_id", "parts_list"]
        for field in required_fields:
            if field not in data:
                return jsonify(
                    {
                        "code": 400, 
                        "message": f"Missing required field: {field}"
                    }
                ), 400
                
        # Create a new delivery
        new_delivery = Delivery(
            id=str(uuid.uuid4()),
            order_id=data["order_id"],
            customer_id=data["customer_id"],
            parts_list=json.dumps(data["parts_list"])  # Serialize to JSON string
        )
        db.session.add(new_delivery)
        db.session.commit()
        
        return jsonify(
            {
                "code": 201,
                "message": "Delivery created successfully",
                "data": {
                    "delivery_id": new_delivery.id,
                    "order_id": new_delivery.order_id,
                    "customer_id": new_delivery.customer_id,
                    "parts_list": json.loads(new_delivery.parts_list),  # Deserialize JSON string
                    "timestamp": new_delivery.timestamp.isoformat()
                }
            }
        ), 201
        
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

def store_delivery_to_db(data):
    # Generate a unique delivery_id
    delivery_id = str(uuid.uuid4())
    
    # Structure the received data in JSON format to store to PostgreSQL
    new_delivery = Delivery(
        id=delivery_id,
        order_id=data["order_id"],
        customer_id=data["customer_id"],
        parts_list=json.dumps(data.get("parts_list", "N/A")),  # Serialize to JSON string
        timestamp=datetime.utcnow()
    )
    db.session.add(new_delivery)
    db.session.commit()

def callback(channel, method, properties, body):
    # Processes incoming deliveries and stores them in PostgreSQL
    try:
        data = json.loads(body)
        store_delivery_to_db(data)
        channel.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message
        print("Update to PostgreSQL successful")
        
    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"Error message: {body}")
    print()

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
    app.run(host='0.0.0.0', port=5003)
    try:
        start_consumer()
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")


