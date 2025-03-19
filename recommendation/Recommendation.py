from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid
from datetime import datetime
import os
import json

app = Flask(__name__)
CORS(app)

# Database configuration
db_host = os.getenv('DB_HOST', 'localhost')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:iloveESD123@{db_host}:5432/recommendation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the Recommendation model
class Recommendation(db.Model):
    id = db.Column(db.String, primary_key=True)
    customer_id = db.Column(db.String, nullable=False)
    parts_list = db.Column(db.Text, nullable=False)  # Store as JSON string
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route("/recommendation/<string:recommendation_id>", methods=['GET'])
def get_recommendation(recommendation_id):
    # Retrieve recommendation from PostgreSQL
    recommendation = Recommendation.query.get(recommendation_id)
    if recommendation:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "recommendation_id": recommendation.id,
                    "customer_id": recommendation.customer_id,
                    "parts_list": json.loads(recommendation.parts_list),  # Deserialize JSON string
                    "timestamp": recommendation.timestamp.isoformat()
                }
            }
        ), 200
    else:
        return jsonify(
            {
                "code": 404,
                "message": "Recommendation not found"
            }
        ), 404

@app.route("/recommendation", methods=['POST'])
def create_recommendation():
    try:
        data = request.get_json()  # Extract JSON data passed in when user creates a recommendation
        
        # Validate fields to be passed on to recommendation JSON format
        required_fields = ["customer_id", "parts_list"]
        for field in required_fields:
            if field not in data:
                return jsonify(
                    {
                        "code": 400, 
                        "message": f"Missing required field: {field}"
                    }
                ), 400
                
        # Create a new recommendation
        new_recommendation = Recommendation(
            id=str(uuid.uuid4()),
            customer_id=data["customer_id"],
            parts_list=json.dumps(data["parts_list"])  # Serialize to JSON string
        )
        db.session.add(new_recommendation)
        db.session.commit()
        
        return jsonify(
            {
                "code": 201,
                "message": "Recommendation created successfully",
                "data": {
                    "recommendation_id": new_recommendation.id,
                    "customer_id": new_recommendation.customer_id,
                    "parts_list": json.loads(new_recommendation.parts_list),  # Deserialize JSON string
                    "timestamp": new_recommendation.timestamp.isoformat()
                }
            }
        ), 201
        
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)