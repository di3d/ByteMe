from flask import Flask, jsonify
import requests
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS if needed

# Your OutSystems API base URL
OUTSYSTEMS_API_BASE = "https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI"

@app.route('/get_components/<category>', methods=['GET'])
def get_components(category):
    try:
        # Construct the full API URL
        api_url = f"{OUTSYSTEMS_API_BASE}/FilterComponentByCategory?category={category}"
        
        # Make the GET request to OutSystems API
        response = requests.get(api_url)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Get the JSON response
        components = response.json()
        
        # Print to console
        print("API Response:")
        print(json.dumps(components, indent=2))
        
        return jsonify({
            "status": "success",
            "data": components
        })
    
    except requests.exceptions.RequestException as e:
        print(f"Error calling OutSystems API: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)