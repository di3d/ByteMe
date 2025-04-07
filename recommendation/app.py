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
    "dbname": os.getenv("DB_NAME", "recommendation_db"),
    "user": os.getenv("DB_USER", "esduser"),
    "password": os.getenv("DB_PASSWORD", "esduser"),
    "host": os.getenv("DB_HOST", "postgres.yanservers.com"),  # Special DNS name to access host
    "port": os.getenv("DB_PORT", "5432"),  # Your host PostgreSQL port
}


def ensure_database_exists():
    """Ensure the recommendation_db database exists"""
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

@app.route("/recommendation/<string:recommendation_id>", methods=['GET'])
def get_recommendation(recommendation_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT recommendation_id, customer_id, name, parts_list, cost, timestamp
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
                    "name": recommendation_data[2],
                    "parts_list": json.loads(recommendation_data[3]),  # Return the parts_list as a list of Ids
                    "cost": float(recommendation_data[4]),
                    "timestamp": recommendation_data[5].isoformat()
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
        required_fields = ["customer_id", "name", "parts_list", "cost"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400, 
                    "message": f"Missing required field: {field}"
                }), 400
                
        # Validate parts_list is an object (dictionary) with part objects containing an 'Id' attribute
        if not isinstance(data["parts_list"], dict) or not all("Id" in part for part in data["parts_list"].values()):
            return jsonify({
                "code": 400,
                "message": "parts_list must be an object where each value contains an 'Id' attribute"
            }), 400

        # Transform parts_list to a list of 'Id' values
        transformed_parts_list = [part["Id"] for part in data["parts_list"].values()]

        # Validate cost is a positive number
        if not isinstance(data["cost"], (int, float)) or data["cost"] < 0:
            return jsonify({
                "code": 400,
                "message": "cost must be a positive number"
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
                recommendation_id, customer_id, name, parts_list, cost, timestamp
            ) VALUES (%s, %s, %s, %s::jsonb, %s, %s)
            RETURNING *
            """,
            (
                recommendation_id,
                data["customer_id"],
                data["name"],
                json.dumps(transformed_parts_list),  # Save the transformed parts_list as a JSON array
                data["cost"],
                current_time
            )
        )
        
        new_recommendation = cursor.fetchone()
        
        if not new_recommendation:
            return jsonify({
                "code": 500,
                "message": "Failed to retrieve the inserted recommendation"
            }), 500
        
        print("New Recommendation:", new_recommendation)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "code": 201,
            "message": "Recommendation created successfully",
            "data": {
                "recommendation_id": new_recommendation[0],
                "customer_id": new_recommendation[1],
                "name": new_recommendation[2],
                "cost": float(new_recommendation[3]),
                "parts_list": transformed_parts_list,  # Return the transformed parts_list
                "timestamp": new_recommendation[5].isoformat()
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

@app.route("/recommendation/customer/<string:customer_id>", methods=['GET'])
def get_recommendations_by_customer(customer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to get all recommendations for the given customer_id
        cursor.execute("""
            SELECT recommendation_id, customer_id, name, parts_list, cost, timestamp
            FROM recommendations
            WHERE customer_id = %s
        """, (customer_id,))
        recommendations = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if recommendations:
            # Format the response data
            recommendations_list = [
                {
                    "recommendation_id": rec[0],
                    "customer_id": rec[1],
                    "name": rec[2],
                    "parts_list": json.loads(rec[3]),  # Return the parts_list as a list of Ids
                    "cost": float(rec[4]),
                    "timestamp": rec[5].isoformat()
                }
                for rec in recommendations
            ]
            return jsonify({
                "code": 200,
                "data": recommendations_list
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": "No recommendations found for the given customer ID"
            }), 404
            
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500
    
@app.route("/recommendation/all", methods=['GET'])
def get_all_recommendations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to get all recommendations for the given customer_id
        cursor.execute("""
            SELECT *
            FROM recommendations
        """)
        recommendations = cursor.fetchall()
        
        cursor.close()
        conn.close()

        if recommendations:
            # Format the response data
            print(recommendations)
            recommendations_list = []
            for rec in recommendations:
                recommendations_list.append(rec)
           
            return jsonify({
                "code": 200,
                "data": recommendations_list
            }), 200
        else:
            return jsonify({
                "code": 404,
                "message": "No recommendations found! Is the database empty?"
            }), 404
    
    except Exception as e:
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
        print(f"Failed to initialize database: {str(e)}")
        exit(1)
    
    app.run(host='0.0.0.0', port=5004, debug=True)