from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

app = Flask(__name__)
CORS(app)

# Database connection parameters
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "customer_db"),
    "user": os.getenv("DB_USER", "esduser"),
    "password": os.getenv("DB_PASSWORD", "esduser"),
    "host": os.getenv("DB_HOST", "localhost"),  # Special DNS name to access host
    "port": os.getenv("DB_PORT", "5444"),  # Your host PostgreSQL port
}

def ensure_database_exists():
    """Ensure the customer_db database exists"""
    try:
        conn = psycopg2.connect(
            dbname=DB_PARAMS["dbname"],
            user=DB_PARAMS["user"],
            password=DB_PARAMS["password"],
            host=DB_PARAMS["host"],
            port=DB_PARAMS["port"]
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'customer_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'customer_db'...")
            cursor.execute("CREATE DATABASE customer_db")
            print("Database 'customer_db' created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error ensuring database exists: {str(e)}")
        raise

def get_db_connection():
    """Get connection to our application database"""
    ensure_database_exists()
    conn = psycopg2.connect(**DB_PARAMS)
    return conn

@app.route("/customers", methods=['GET'])
def get_all_customers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT customer_id, name, address, email 
            FROM customers 
            ORDER BY customer_id
        """)
        customers_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if customers_data:
            customers = []
            for customer in customers_data:
                customers.append({
                    "customer_id": customer[0],
                    "name": customer[1],
                    "address": customer[2],
                    "email": customer[3]
                })
            
            return jsonify({
                "code": 200,
                "data": customers
            }), 200
        else:
            return jsonify({
                "code": 200,
                "data": [],
                "message": "No customers found"
            }), 200
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500
        

@app.route("/customer/<string:customer_id>", methods=['GET'])
def get_customer(customer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT customer_id, name, address, email 
            FROM customers 
            WHERE customer_id = %s
        """, (customer_id,))
        customer_data = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if customer_data:
            return jsonify({
                "code": 200,
                "data": {
                    "customer_id": customer_data[0],
                    "name": customer_data[1],
                    "address": customer_data[2],
                    "email": customer_data[3]
                }
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": "Customer not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500

@app.route("/customer", methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["customer_id", "name", "address", "email"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400, 
                    "message": f"Missing required field: {field}"
                }), 400
                
        # Check if customer already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id FROM customers WHERE customer_id = %s", (data["customer_id"],))
        if cursor.fetchone():
            # Update existing customer
            cursor.execute(
                """
                UPDATE customers 
                SET name = %s, address = %s, email = %s
                WHERE customer_id = %s
                RETURNING customer_id, name, address, email
                """,
                (
                    data["name"],
                    data["address"],
                    data["email"],
                    data["customer_id"]
                )
            )
            
            updated_customer = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                "code": 200,
                "message": "Customer updated successfully",
                "data": {
                    "customer_id": updated_customer[0],
                    "name": updated_customer[1],
                    "address": updated_customer[2],
                    "email": updated_customer[3]
                }
            }), 200
        
        # Create new customer
        cursor.execute(
            """
            INSERT INTO customers (customer_id, name, address, email)
            VALUES (%s, %s, %s, %s)
            RETURNING customer_id, name, address, email
            """,
            (
                data["customer_id"],
                data["name"],
                data["address"],
                data["email"]
            )
        )
        
        new_customer = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "code": 201,
            "message": "Customer created successfully",
            "data": {
                "customer_id": new_customer[0],
                "name": new_customer[1],
                "address": new_customer[2],
                "email": new_customer[3]
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

@app.route("/customer/<string:customer_id>", methods=['PUT'])
def update_customer(customer_id):
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["name", "address", "email"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400,
                    "message": f"Missing required field: {field}"
                }), 400

        # Update customer details in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            UPDATE customers
            SET name = %s, address = %s, email = %s
            WHERE customer_id = %s
            RETURNING customer_id, name, address, email
            """,
            (
                data["name"],
                data["address"],
                data["email"],
                customer_id
            )
        )
        
        updated_customer = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if updated_customer:
            return jsonify({
                "code": 200,
                "message": "Customer updated successfully",
                "data": {
                    "customer_id": updated_customer[0],
                    "name": updated_customer[1],
                    "address": updated_customer[2],
                    "email": updated_customer[3]
                }
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": "Customer not found"
            }), 404

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
    try:
        ensure_database_exists()
        # initialize_tables()
    except Exception as e:
        print(f"Failed to find database: {str(e)}")
        exit(1)
    
    app.run(host='0.0.0.0', port=5001)