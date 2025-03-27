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
    "dbname": os.getenv("DB_NAME", "customer_db"),
    "user": os.getenv("DB_USER", "esduser"),
    "password": os.getenv("DB_PASSWORD", "esduser"),
    "host": os.getenv("DB_HOST", "localhost"),  # Special DNS name to access host
    "port": os.getenv("DB_PORT", "5444"),  # Your host PostgreSQL port
}


def ensure_database_exists():
    """Ensure the recommendation_db database exists"""
    try:
        # Connect to the default 'postgres' database to check/create our database
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_PARAMS["user"],
            password=DB_PARAMS["password"],
            host=DB_PARAMS["host"],
            port=DB_PARAMS["port"]
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'recommendation_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'recommendation_db'...")
            cursor.execute("CREATE DATABASE recommendation_db")
            print("Database 'recommendation_db' created successfully")
        
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
    """Initialize the database tables for recommendation service"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Recommendation table schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id VARCHAR PRIMARY KEY,
                customer_id VARCHAR NOT NULL,
                parts_list JSONB NOT NULL,
                timestamp TIMESTAMP NOT NULL
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Recommendation tables initialized successfully")
    except Exception as e:
        print(f"Error initializing recommendation tables: {str(e)}")
        raise

@app.route("/recommendation/<string:recommendation_id>", methods=['GET'])
def get_recommendation(recommendation_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT recommendation_id, customer_id, parts_list, timestamp
            FROM recommendations 
            WHERE recommendation_id = %s
        """, (recommendation_id,))
        recommendation_data = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if recommendation_data:
            return jsonify({
                "code": 200,
                "data": {
                    "recommendation_id": recommendation_data[0],
                    "customer_id": recommendation_data[1],
                    "parts_list": recommendation_data[2],
                    "timestamp": recommendation_data[3].isoformat()
                }
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": "Recommendation not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500

@app.route("/recommendation", methods=['POST'])
def create_recommendation():
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
                
        # Generate recommendation_id and timestamp
        recommendation_id = str(uuid.uuid4())
        current_time = datetime.now()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create new recommendation
        cursor.execute(
            """
            INSERT INTO recommendations (
                recommendation_id, customer_id, parts_list, timestamp
            ) VALUES (%s, %s, %s::jsonb, %s)
            RETURNING *
            """,
            (
                recommendation_id,
                data["customer_id"],
                json.dumps(data["parts_list"]),
                current_time
            )
        )
        
        new_recommendation = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "code": 201,
            "message": "Recommendation created successfully",
            "data": {
                "recommendation_id": new_recommendation[0],
                "customer_id": new_recommendation[1],
                "parts_list": new_recommendation[2],
                "timestamp": new_recommendation[3].isoformat()
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

if __name__ == '__main__':
    # First ensure database exists, then initialize tables
    try:
        ensure_database_exists()
        initialize_tables()
    except Exception as e:
        print(f"Failed to initialize database: {str(e)}")
        exit(1)
    
    app.run(host='0.0.0.0', port=5004)