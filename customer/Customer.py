from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

app = Flask(__name__)
CORS(app)

# Fetch the service account key JSON file contents
cred = credentials.Certificate('./privateKey.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://esdteam3g7-73a7b-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('Customers')


@app.route("/customer/<string:customer_id>", methods=['GET'])
def getCustomer(customer_id):
    customer = ref.child(customer_id).get()
    if customer:
        return jsonify(
            {
                "code": 200,
                "data": customer
            }
        ), 200
        
    else: 
        return jsonify(
            {
                "code": 404,
                "data": "Customer not found"
            }
        ), 404

@app.route("/customer", methods=['POST'])
def create_customer():
    try:
        data = request.get_json() #extact json data passed in when user creates an account
        
        #validate fields to be passed on to customer JSON format
        required_fields = ["customer_id", "name", "address", "email" ]
        for field in required_fields:
            if field not in data:
                return jsonify(
                    {
                        "code": 400, 
                        "message": f"Missing required field: {field}"
                    }
                ), 400
                
        #json structure to be passed to db
        customer_id = data["customer_id"]
        customer_data = {
            "name":data["name"],
            "address":data["address"],
            "email":data["email"]
        }
        
        #store in fb
        ref.child(customer_id).set(customer_data)
        
        return jsonify (
            {
                "code":201,
                "message":"Customer created successfully",
                "data":customer_data
            }
        ), 201
        
        
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
    



if __name__ == '__main__':
    # app.run(port=5004, debug=True)
    app.run(host='0.0.0.0', port=5006)
    