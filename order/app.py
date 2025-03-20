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

        # Publish the order to RabbitMQ
        order_message = {
            "order_id": new_order.id,
            "customer_id": new_order.customer_id,
            "parts_list": new_order.parts_list,
            "timestamp": new_order.timestamp.isoformat(),
            "status": new_order.status
        }
        amqp_setup.publish_message(
            exchange_name="order_topic",
            routing_key="order.create",
            message=json.dumps(order_message)
        )

        return jsonify(
            {
                "code": 201,
                "message": "Order created successfully",
                "data": order_message
            }
        ), 201
        
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

def store_order_to_db(data):
    new_order = Order(
        id=data["order_id"],
        customer_id=data["customer_id"],
        parts_list=data["parts_list"],
        timestamp=datetime.fromisoformat(data["timestamp"]),
        status=data["status"]
    )
    db.session.add(new_order)
    db.session.commit()

def callback(channel, method, properties, body):
    try:
        data = json.loads(body)
        store_order_to_db(data)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        print("Order stored to PostgreSQL successfully")
    except Exception as e:
        print(f"Error processing message: {e}")
        print(f"Message body: {body}")

def start_consumer():
    connection, channel = amqp_setup.get_connection_and_channel()
    channel.basic_consume(queue="Order", on_message_callback=callback, auto_ack=False)
    print("Starting RabbitMQ consumer...")
    channel.start_consuming()

if __name__ == '__main__':
    import threading
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
    app.run(host='0.0.0.0', port=5002)


