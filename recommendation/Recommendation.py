from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid
from datetime import datetime
import sys
import os
import json
from sqlalchemy.dialects.postgresql import JSON

app = Flask(__name__)
CORS(app)

# Database configuration
db_host = os.getenv('DB_HOST', 'localhost')
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:iloveESD123@{db_host}:5432/customer'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the Customer model
class Recommendation(db.Model):
    id = db.Column(db.String, primary_key=True)
    customer_id = db.Column(db.String, nullable=False)
    parts_list = db.Column(JSON, nullable=False)
    
@app.route("/recommendation", methods=['GET'])
def getAllRecommendation():
    recommendation_list = Recommendation.query.all()
    if len(recommendation_list):
        return jsonify(
            {
                "code":200,
                "data": {
                    "recommendations":[
                        {
                            "recommendation_id": recommendation.id,
                            "customer_id": recommendation.customer_id,
                            "parts_list": recommendation.parts_list,
                        } for recommendation in recommendation_list
                    ]
                }
            }
        ), 200
        
    else: 
        return jsonify(
            {
                "code": 404,
                "message": "There are no recommendations"
            }
        ), 404
    

@app.route("/recommendation/<string:recommendation_id>", methods=['GET'])
def getRecommendation(recommnedation_id):
    # Retrieve customer from PostgreSQL
    recommendation = Recommendation.query.get(recommnedation_id)
    if recommendation:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "recommendation_id": recommendation.id,
                    "customer_id": recommendation.customer_id,
                    "parts_list": recommendation.parts_list,
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
        data = request.get_json()  # Extract JSON data passed in when user creates an account
        
        # Validate fields to be passed on to customer JSON format
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
            parts_list=data["parts_list"],
        )
        db.session.add(new_recommendation)
        db.session.commit()
        
        return jsonify(
            {
                "code": 201,
                "message": "Customer created successfully",
                "data": {
                    "recommendation_id": new_recommendation.id,
                    "customer_id": new_recommendation.customer_id,
                    "parts_list": new_recommendation.parts_list,
                }
            }
        ), 201
        
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
