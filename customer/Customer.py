from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)

# Database configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:iloveESD123@localhost:5432/customer'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:iloveESD123@host.docker.internal:5432/customer'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the Customer model
class Customer(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

@app.route("/customer/<string:customer_id>", methods=['GET'])
def getCustomer(customer_id):
    # Retrieve customer from PostgreSQL
    customer = Customer.query.get(customer_id)
    if customer:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "customer_id": customer.id,
                    "name": customer.name,
                    "address": customer.address,
                    "email": customer.email
                }
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
                
        # Check if the customer already exists
        if Customer.query.get(data["customer_id"]):
            return jsonify(
                {
                    "code": 409,
                    "message": "Customer already exists"
                }
            ), 409
        
        # Create a new customer
        new_customer = Customer(
            id=data["customer_id"],
            name=data["name"],
            address=data["address"],
            email=data["email"]
        )
        db.session.add(new_customer)
        db.session.commit()
        
        return jsonify(
            {
                "code": 201,
                "message": "Customer created successfully",
                "data": {
                    "customer_id": new_customer.id,
                    "name": new_customer.name,
                    "address": new_customer.address,
                    "email": new_customer.email
                }
            }
        ), 201
        
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
