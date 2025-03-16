from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

# Fetch the service account key JSON file contents
cred = credentials.Certificate('./privateKey.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred)

# Get Firestore database reference
db = firestore.client()  # Firestore database reference
customers_ref = db.collection('customer')  # Firestore collection reference

@app.route("/customer/<string:customer_id>", methods=['GET'])
def getCustomer(customer_id):
    # Retrieve customer document from Firestore
    customer_doc = customers_ref.document(customer_id).get()
    if customer_doc.exists:
        return jsonify(
            {
                "code": 200,
                "data": customer_doc.to_dict()  # Convert document to dictionary format
            }
        ), 200
        
    else: 
        return jsonify(
            {
                "code": 404,
                "message": "Customer not found"
            }
        ), 404

@app.route("/customer", methods=['POST'])
def create_customer():
    try:
        data = request.get_json()  # Extract JSON data passed in when user creates an account
        
        # Validate fields to be passed on to customer JSON format
        required_fields = ["customer_id", "name", "address", "email"]
        for field in required_fields:
            if field not in data:
                return jsonify(
                    {
                        "code": 400, 
                        "message": f"Missing required field: {field}"
                    }
                ), 400
                
        # JSON structure to be passed to Firestore
        customer_id = data["customer_id"]
        customer_data = {
            "name": data["name"],
            "address": data["address"],
            "email": data["email"]
        }
        
        # Check if the document exists
        customer_doc = customers_ref.document(customer_id).get()
        if customer_doc.exists:
            return jsonify(
                {
                    "code": 409,
                    "message": "Customer already exists"
                }
            ), 409
        
        # Store in Firestore
        customers_ref.document(customer_id).set(customer_data)
        
        return jsonify(
            {
                "code": 201,
                "message": "Customer created successfully",
                "data": customer_data
            }
        ), 201
        
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


if __name__ == '__main__':
    # app.run(port=5004, debug=True)
    app.run(host='0.0.0.0', port=5006)
