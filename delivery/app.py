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
    "dbname": os.getenv("DB_NAME", "delivery_db"),
    "user": os.getenv("DB_USER", "esduser"),
    "password": os.getenv("DB_PASSWORD", "esduser"),
    "host": os.getenv("DB_HOST", "localhost"),  # Special DNS name to access host
    "port": os.getenv("DB_PORT", "5444"),  # Your host PostgreSQL port
}


def ensure_database_exists():
    """Ensure the delivery_db database exists"""
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
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'delivery_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'delivery_db'...")
            cursor.execute("CREATE DATABASE delivery_db")
            print("Database 'delivery_db' created successfully")
        
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

# def initialize_tables():
#     """Initialize the database tables for delivery service"""
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         # Updated table schema with parts_list (JSON) and timestamp
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS deliveries (
#                 delivery_id VARCHAR PRIMARY KEY,
#                 order_id VARCHAR NOT NULL,
#                 customer_id VARCHAR NOT NULL,
#                 parts_list JSONB NOT NULL,
#                 created_at TIMESTAMP NOT NULL,
#                 updated_at TIMESTAMP NOT NULL
#             )
#         """)
#         conn.commit()
#         cursor.close()
#         conn.close()
#         print("Delivery tables initialized successfully")
#     except Exception as e:
#         print(f"Error initializing delivery tables: {str(e)}")
#         raise

@app.route("/delivery/<string:delivery_id>", methods=['GET'])
def get_delivery(delivery_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT delivery_id, order_id, customer_id, 
                created_at, updated_at
            FROM deliveries 
            WHERE delivery_id = %s
        """, (delivery_id,))
        delivery_data = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if delivery_data:
            return jsonify({
                "code": 200,
                "data": {
                    "delivery_id": delivery_data[0],
                    "order_id": delivery_data[1],
                    "customer_id": delivery_data[2],
                    "created_at": delivery_data[3].isoformat(),
                    "updated_at": delivery_data[4].isoformat()
                }
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": "Delivery not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500

@app.route("/delivery", methods=['POST'])
def create_delivery():
    try:
        data = request.get_json()
        
        # Validate fields
        required_fields = ["order_id", "customer_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400, 
                    "message": f"Missing required field: {field}"
                }), 400
                
        # Generate delivery_id and timestamp
        delivery_id = str(uuid.uuid4())
        current_time = datetime.now()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create new delivery with auto-generated fields
        cursor.execute(
            """
            INSERT INTO deliveries (
                delivery_id, order_id, customer_id,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                delivery_id,
                data["order_id"],
                data["customer_id"],
                current_time,
                current_time
            )
        )
        
        new_delivery = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "code": 201,
            "message": "Delivery created successfully",
            "data": {
                "delivery_id": new_delivery[0],
                "order_id": new_delivery[1],
                "customer_id": new_delivery[2],
                "created_at": new_delivery[3].isoformat(),
                "updated_at": new_delivery[4].isoformat()
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

@app.route("/delivery/<string:delivery_id>", methods=['PUT'])
def update_delivery(delivery_id):
    try:
        data = request.get_json()
        current_time = datetime.now()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update only the fields that are provided
        update_fields = []
        update_values = []
        
        if "order_id" in data:
            update_fields.append("order_id = %s")
            update_values.append(data["order_id"])
            
        if "customer_id" in data:
            update_fields.append("customer_id = %s")
            update_values.append(data["customer_id"])
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = %s")
        update_values.append(current_time)
        
        if not update_fields:
            return jsonify({
                "code": 400,
                "message": "No fields to update"
            }), 400
            
        update_query = f"""
            UPDATE deliveries 
            SET {', '.join(update_fields)}
            WHERE delivery_id = %s
            RETURNING *
        """
        update_values.append(delivery_id)
        
        cursor.execute(update_query, update_values)
        updated_delivery = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if not updated_delivery:
            return jsonify({
                "code": 404,
                "message": "Delivery not found"
            }), 404
            
        return jsonify({
            "code": 200,
            "message": "Delivery updated successfully",
            "data": {
                "delivery_id": updated_delivery[0],
                "order_id": updated_delivery[1],
                "customer_id": updated_delivery[2],
                "created_at": updated_delivery[3].isoformat(),
                "updated_at": updated_delivery[4].isoformat()
            }
        }), 200
        
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
    # First ensure database exists, then initialize tables
    try:
        ensure_database_exists()
        # initialize_tables()
    except Exception as e:
        print(f"Failed to detect database: {str(e)}")
        exit(1)
    
    app.run(host='0.0.0.0', port=5003)