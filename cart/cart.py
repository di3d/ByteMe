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
    "dbname": os.getenv("DB_NAME", "cart_db"),
    "user": os.getenv("DB_USER", "esduser"),
    "password": os.getenv("DB_PASSWORD", "esduser"),
    "host": os.getenv("DB_HOST", "postgres.yanservers.com"),  # Special DNS name to access host
    "port": os.getenv("DB_PORT", "5432"),  # Your host PostgreSQL port
}

def get_db_connection():
    """Returns a connection to the database."""
    conn = psycopg2.connect(**DB_PARAMS)
    return conn

def ensure_database_exists():
    """Ensures that the cart_db database exists."""
    try:
        conn = psycopg2.connect(
            dbname="postgres", user=DB_PARAMS["user"],
            password=DB_PARAMS["password"], host=DB_PARAMS["host"], port=DB_PARAMS["port"]
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'cart_db'")
        if not cursor.fetchone():
            print("Creating database 'cart_db'...")
            cursor.execute("CREATE DATABASE cart_db")
            print("Database 'cart_db' created successfully")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error ensuring database exists: {str(e)}")
        raise

def ensure_carts_table_exists():
    """Ensures that the carts table exists in the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carts (
                cart_id UUID PRIMARY KEY,
                customer_id VARCHAR(100) NOT NULL,
                name VARCHAR(255) NOT NULL,
                parts_list JSONB NOT NULL,
                total_cost NUMERIC(10, 2) NOT NULL,
                timestamp TIMESTAMP NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Checked for 'carts' table and created it if missing.")
    except Exception as e:
        print(f"Error ensuring carts table exists: {str(e)}")
        raise


def transform_parts_list(parts_list):
    """Transforms the parts_list into a list of 'Id' values."""
    if isinstance(parts_list, dict) and all("Id" in part for part in parts_list.values()):
        return [part["Id"] for part in parts_list.values()]
    else:
        raise ValueError("parts_list must be an object where each value contains an 'Id' attribute")

def execute_query(query, params):
    """Executes a database query and returns the results."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        raise Exception(f"Database query failed: {str(e)}")

# Endpoint to fetch a cart by cart_id
@app.route("/cart/<string:cart_id>", methods=['GET'])
def get_cart(cart_id):
    query = """
        SELECT cart_id, customer_id, name, parts_list, total_cost, timestamp
        FROM carts 
        WHERE cart_id = %s
    """
    result = execute_query(query, (cart_id,))
    if result:
        cart = result[0]
        return jsonify({
            "code": 200,
            "data": {
                "cart_id": cart[0],
                "customer_id": cart[1],
                "name": cart[2],
                "parts_list": cart[3],  # List of parts as-is
                "total_cost": float(cart[4]),
                "timestamp": cart[5].isoformat()
            }
        }), 200
    else:
        return jsonify({
            "code": 404,
            "message": "Cart not found"
        }), 404

# Endpoint to create a new cart
@app.route("/cart", methods=['POST'])
def create_cart():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["customer_id", "name", "parts_list", "total_cost"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400, 
                    "message": f"Missing required field: {field}"
                }), 400
                
        # Transform parts_list
        try:
            transformed_parts_list = transform_parts_list(data["parts_list"])
        except ValueError as e:
            return jsonify({
                "code": 400,
                "message": str(e)
            }), 400

        # Validate total_cost is a positive number
        if not isinstance(data["total_cost"], (int, float)) or data["total_cost"] < 0:
            return jsonify({
                "code": 400,
                "message": "total_cost must be a positive number"
            }), 400
        
        cart_id = str(uuid.uuid4())
        current_time = datetime.now()
        
        # Insert new cart into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO carts (
                cart_id, customer_id, name, parts_list, total_cost, timestamp
            ) VALUES (%s, %s, %s, %s::jsonb, %s, %s)
            RETURNING *
            """,
            (
                cart_id,
                data["customer_id"],
                data["name"],
                json.dumps(transformed_parts_list),  # Store parts list as JSON
                data["total_cost"],
                current_time
            )
        )
        
        new_cart = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "code": 201,
            "message": "Cart created successfully",
            "data": {
                "cart_id": new_cart[0],
                "customer_id": new_cart[1],
                "name": new_cart[2],
                "total_cost": float(new_cart[3]),
                "parts_list": transformed_parts_list,  # Return the transformed parts list
                "timestamp": new_cart[5].isoformat()
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500

# Endpoint to get carts by customer
@app.route("/cart/customer/<string:customer_id>", methods=['GET'])
def get_carts_by_customer(customer_id):
    query = """
        SELECT cart_id, customer_id, name, parts_list, total_cost, timestamp
        FROM carts
        WHERE customer_id = %s
    """
    carts = execute_query(query, (customer_id,))
    if carts:
        carts_list = [
            {
                "cart_id": cart[0],
                "customer_id": cart[1],
                "name": cart[2],
                "parts_list": cart[3],  # Directly return parts list
                "total_cost": float(cart[4]),
                "timestamp": cart[5].isoformat()
            }
            for cart in carts
        ]
        return jsonify({
            "code": 200,
            "data": carts_list
        }), 200
    else:
        return jsonify({
            "code": 404,
            "message": "No carts found for the given customer ID"
        }), 404

# Endpoint to get all carts
@app.route("/cart/all", methods=['GET'])
def get_all_carts():
    query = """
        SELECT cart_id, customer_id, name, parts_list, total_cost, timestamp
        FROM carts
    """
    carts = execute_query(query, ())
    if carts:
        carts_list = [
            {
                "cart_id": cart[0],
                "customer_id": cart[1],
                "name": cart[2],
                "parts_list": cart[3],  # Directly return parts list
                "total_cost": float(cart[4]),
                "timestamp": cart[5].isoformat()
            }
            for cart in carts
        ]
        return jsonify({
            "code": 200,
            "data": carts_list
        }), 200
    else:
        return jsonify({
            "code": 404,
            "message": "No carts found! Is the database empty?"
        }), 404

if __name__ == '__main__':
    try:
        ensure_database_exists()
        ensure_carts_table_exists()  # <-- Add this
    except Exception as e:
        print(f"Failed to initialize database or table: {str(e)}")
        exit(1)

    app.run(host='0.0.0.0', port=5004, debug=True)

