from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
import json
import uuid
from datetime import datetime
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

app = Flask(__name__)
CORS(app)

# Database connection parameters
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "order_db"),
    "user": os.getenv("DB_USER", "esduser"),
    "password": os.getenv("DB_PASSWORD", "esduser"),
    "host": os.getenv("DB_HOST", "localhost"),  # Special DNS name to access host
    "port": os.getenv("DB_PORT", "5444"),  # Your host PostgreSQL port
}


def ensure_database_exists():
    """Ensure the order_db database exists"""
    try:
        # Connect to the default 'postgres' database to check/create our database
        conn = psycopg2.connect(
            dbname=DB_PARAMS["dbname"],
            user=DB_PARAMS["user"],
            password=DB_PARAMS["password"],
            host=DB_PARAMS["host"],
            port=DB_PARAMS["port"]
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'order_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'order_db'...")
            cursor.execute("CREATE DATABASE order_db")
            print("Database 'order_db' created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error ensuring database exists: {str(e)}")
        raise

def get_db_connection():
    """Get connection to our application database"""
    ensure_database_exists()  # Make sure DB exists before connecting
    conn = psycopg2.connect(**DB_PARAMS)
    return conn

def initialize_tables():
    """Initialize the database tables for order service"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Simplified order table schema doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id VARCHAR PRIMARY KEY,
                customer_id VARCHAR NOT NULL,
                parts_list JSONB NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                timestamp TIMESTAMP NOT NULL
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Order tables initialized successfully")
    except Exception as e:
        print(f"Error initializing order tables: {str(e)}")
        raise

@app.route("/order/<string:order_id>", methods=['GET'])
def get_order(order_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT order_id, customer_id, parts_list, status, timestamp
            FROM orders 
            WHERE order_id = %s
        """, (order_id,))
        order_data = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if order_data:
            return jsonify({
                "code": 200,
                "data": {
                    "order_id": order_data[0],
                    "customer_id": order_data[1],
                    "parts_list": order_data[2],
                    "status": order_data[3],
                    "timestamp": order_data[4].isoformat()
                }
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": "Order not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500
        
@app.route("/order/customers/<string:customer_id>", methods=['GET'])
def get_orders_by_customer(customer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT order_id, customer_id, parts_list, status, timestamp
            FROM orders 
            WHERE customer_id = %s
        """, (customer_id,))
        orders_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if orders_data:
            orders = []
            for order in orders_data:
                orders.append({
                    "order_id": order[0],
                    "customer_id": order[1],
                    "parts_list": order[2],
                    "status": order[3],
                    "timestamp": order[4].isoformat()
                })
            
            return jsonify({
                "code": 200,
                "data": orders
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": "No orders found for this customer"
            }), 404
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500

@app.route("/order", methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["customer_id", "parts_list"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400, 
                    "message": f"Missing required field: {field}"
                }), 400
                
        # Validate parts_list is a list
        if not isinstance(data["parts_list"], list):
            return jsonify({
                "code": 400,
                "message": "parts_list must be an array"
            }), 400
                
        # Generate order_id and timestamp
        order_id = data.get("order_id")
        current_time = datetime.now()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create new order with default status 'pending'
        cursor.execute(
            """
            INSERT INTO orders (
                order_id, customer_id, parts_list, status, timestamp
            ) VALUES (%s, %s, %s::jsonb, %s, %s)
            RETURNING *
            """,
            (
                order_id,
                data["customer_id"],
                json.dumps(data["parts_list"]),
                "pending",  # Default status
                current_time
            )
        )
        
        new_order = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "code": 201,
            "message": "Order created successfully",
            "data": {
                "order_id": new_order[0],
                "customer_id": new_order[1],
                "parts_list": new_order[2],
                "status": new_order[3],
                "timestamp": new_order[4].isoformat()
            }
        }), 201
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            if 'cursor' in locals():
                cursor.close()
            conn.close()
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500

@app.route("/order", methods=['GET'])
def get_all_orders():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT order_id, customer_id, parts_list, status, timestamp
            FROM orders
        """)
        orders = cursor.fetchall()  # Fetch all results

        cursor.close()
        conn.close()

        if orders:
            order_list = []
            for order in orders:
                order_list.append({
                    "order_id": order[0],
                    "customer_id": order[1],
                    "parts_list": order[2],
                    "status": order[3],
                    "timestamp": order[4].isoformat()
                })

            return jsonify({
                "code": 200,
                "data": order_list
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": "No orders found"
            }), 404

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500

@app.route("/order/<string:order_id>/status", methods=['PUT'])
def update_order_status(order_id):
    """Update the status of an order"""
    try:
        data = request.get_json()
        
        if "status" not in data:
            return jsonify({
                "code": 400,
                "message": "Missing required field: status"
            }), 400
            
        status = data["status"]
        # Validate status
        valid_statuses = ["pending", "processing", "completed", "refunded", "refund_pending"]
        if status not in valid_statuses:
            return jsonify({
                "code": 400,
                "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if order exists
        cursor.execute("SELECT order_id FROM orders WHERE order_id = %s", (order_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "code": 404,
                "message": "Order not found"
            }), 404
        
        # Update the order status
        cursor.execute(
            """
            UPDATE orders 
            SET status = %s
            WHERE order_id = %s
            RETURNING order_id, customer_id, parts_list, status, timestamp
            """,
            (status, order_id)
        )
        
        updated_order = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if updated_order:
            return jsonify({
                "code": 200,
                "message": "Order status updated successfully",
                "data": {
                    "order_id": updated_order[0],
                    "customer_id": updated_order[1],
                    "parts_list": updated_order[2],
                    "status": updated_order[3],
                    "timestamp": updated_order[4].isoformat()
                }
            }), 200
        else:
            return jsonify({
                "code": 500,
                "message": "Failed to update order status"
            }), 500
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500
        
        
@app.route("/order/<string:order_id>", methods=['DELETE'])
def delete_order(order_id):
    """Delete an order by its ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if order exists first
        cursor.execute("SELECT order_id FROM orders WHERE order_id = %s", (order_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "code": 404,
                "message": "Order not found"
            }), 404
        
        # Delete the order
        cursor.execute(
            """
            DELETE FROM orders 
            WHERE order_id = %s
            RETURNING order_id
            """,
            (order_id,)
        )
        
        deleted_order = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if deleted_order:
            return jsonify({
                "code": 200,
                "message": "Order deleted successfully",
                "data": {
                    "order_id": deleted_order[0]
                }
            }), 200
        else:
            return jsonify({
                "code": 500,
                "message": "Failed to delete order"
            }), 500
            
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            if 'cursor' in locals():
                cursor.close()
            conn.close()
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Only ensure the database exists, no table initialization
    try:
        ensure_database_exists()
    except Exception as e:
        print(f"Failed to ensure database exists: {str(e)}")
        exit(1)
    
    app.run(host='0.0.0.0', port=5002)