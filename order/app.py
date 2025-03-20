import sys
import os

# Add the path to amqp_setup.py for local testing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../amqp')))

# Always import amqp_setup
import amqp_setup

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pika
import uuid
from datetime import datetime
import os
import json
from sqlalchemy.dialects.postgresql import JSON

app = Flask(__name__)
CORS(app)

# Detect if running inside Docker
RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"

# Set Database Configuration Dynamically
if RUNNING_IN_DOCKER:
    DB_HOST = "host.docker.internal"  # Docker network name
    DB_PORT = "5433"
else:
    DB_HOST = "localhost"  # Local environment
    DB_PORT = "5432"


DB_NAME = os.getenv("DB_NAME", "order_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "iloveESD123")

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the Order model
class Order(db.Model):
    id = db.Column(db.String, primary_key=True)
    customer_id = db.Column(db.String, nullable=False)
    parts_list = db.Column(JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String, nullable=False, default="pending")

@app.route("/order/<string:order_id>", methods=['GET'])
def get_order(order_id):
    # Retrieve order from PostgreSQL
    order = Order.query.get(order_id)
    if order:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "order_id": order.id,
                    "customer_id": order.customer_id,
                    "parts_list": order.parts_list,
                    "timestamp": order.timestamp.isoformat(),
                    "status": order.status
                }
            }
        ), 200
    else:
        return jsonify(
            {
                "code": 404,
                "message": "Order not found"
            }
        ), 404

@app.route("/order", methods=['POST'])
def create_order():
    try:
        data = request.get_json()  # Extract JSON data passed in when user creates an order
        
        # Validate fields to be passed on to order JSON format
        required_fields = ["customer_id", "parts_list"]
        for field in required_fields:
            if field not in data:
                return jsonify(
                    {
                        "code": 400, 
                        "message": f"Missing required field: {field}"
                    }
                ), 400
                
        # Create a new order
        new_order = Order(
            id=str(uuid.uuid4()),
            customer_id=data["customer_id"],
            parts_list=data["parts_list"],
            status="pending"
        )
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify(
            {
                "code": 201,
                "message": "Order created successfully",
                "data": {
                    "order_id": new_order.id,
                    "customer_id": new_order.customer_id,
                    "parts_list": new_order.parts_list,
                    "timestamp": new_order.timestamp.isoformat(),
                    "status": new_order.status
                }
            }
        ), 201
        
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

def store_order_to_db(data):
    # Generate a unique order_id
    order_id = str(uuid.uuid4())
    order_date = datetime.utcnow().isoformat()
    
    # Structure the received data in JSON format to store to PostgreSQL
    new_order = Order(
        id=order_id,
        customer_id=data["customer_id"],
        parts_list=data.get("parts_list", "N/A"),
        timestamp=order_date,
        status="pending"
    )
    db.session.add(new_order)
    db.session.commit()

def callback(channel, method, properties, body):
    # Processes incoming orders and stores them in PostgreSQL
    try:
        data = json.loads(body)
        store_order_to_db(data)
        channel.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message
        print("Order stored to PostgreSQL successfully")
        
    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"Error message: {body}")
    print()

@app.route("/start_consumer", methods=["POST"])
def start_consumer():
    amqp_setup.setup_rabbitmq()  # Set up RabbitMQ only when this endpoint is called
    return "RabbitMQ consumer started", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
    try:
        start_consumer()
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")


