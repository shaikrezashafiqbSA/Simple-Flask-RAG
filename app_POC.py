import json
import re
import datetime
from flask import Flask, request, jsonify, Response
import jwt
from flask_cors import CORS

from RAG.traveller import traveller
from responses.static import static_response

app = Flask(__name__)
CORS(app)  



rag = traveller()

def fix_json(text):
    # Regex pattern to find missing commas after activity objects
    pattern = r"(\}\s*){"  
    # Replace missing commas with comma and space
    corrected_text = re.sub(pattern, "}, ", text)
    return corrected_text

def generate_token(user_id):
    secret_key = "314159"  
    payload = {"user_id": user_id} #, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def validate_token(token):
    try:
        secret_key = "314159"  # Replace with your actual secret key
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = payload.get("user_id")
        # Validate user_id or any other relevant checks
        return True
    except jwt.ExpiredSignatureError:
        return False
    
@app.route('/api', methods=['POST'])
def generate_package_from_model():
    if request.method == 'POST':
        bearer_token = request.headers.get('Authorization')
        print(bearer_token)
        if not bearer_token:
            return "Unauthorized", 401

        token = bearer_token.split()[1]  # Extract the actual token
        print(token)
        if not validate_token(token):
            return "Invalid token", 401
        print(request.json) 
        """
        Example:
        request.json = {"destination":"penang",
                        "dates":"August",
                        "duration":"2 days",
                        "number_of_pax":"2",
                        "filter":"foodie, attractions, magical",
                        "budget":"$2000",
                        "prompt":""}
        """
        # try:
        itinerary_payload = rag.generate_travel_itinerary(request.json, version=1)
        print(itinerary_payload)
        try:
            output = json.loads(itinerary_payload["response"].text)
            output["prompt"] = request.json["prompt"]
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error \n{e}\n occurred while generating the travel itinerary", 500  # Internal Server Error
    else:
        return "This endpoint only accepts POST requests", 405  # Method Not Allowed
    
@app.route('/api/2', methods=['POST'])
def generate_package_from_model_V2():
    if request.method == 'POST':
        bearer_token = request.headers.get('Authorization')
        print(bearer_token)
        if not bearer_token:
            return "Unauthorized", 401

        token = bearer_token.split()[1]  # Extract the actual token
        print(token)
        if not validate_token(token):
            return "Invalid token", 401
        print(request.json) 
        """
        Example:
        request.json = {"destination":"penang",
                        "dates":"August",
                        "duration":"2 days",
                        "number_of_pax":"2",
                        "filter":"foodie, attractions, magical",
                        "budget":"$2000",
                        "prompt":""}
        """
        # try:
        itinerary_payload = rag.generate_travel_itinerary(request.json)
        # print(itinerary_payload)
        try:
            corrected_json_text  = fix_json(itinerary_payload["response"].text)
            output = json.loads(corrected_json_text)
            output["prompt"] = request.json["prompt"]
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error \n{e}\n occurred while generating the travel itinerary", 500  # Internal Server Error
    else:
        return "This endpoint only accepts POST requests", 405  # Method Not Allowed


@app.route('/api/0', methods=['POST'])
def generate_package_from_model_pure_LLM():
    if request.method == 'POST':
        bearer_token = request.headers.get('Authorization')
        print(bearer_token)
        if not bearer_token:
            return "Unauthorized", 401

        token = bearer_token.split()[1]  # Extract the actual token
        print(token)
        if not validate_token(token):
            return "Invalid token", 401
        print(request.json) 
        """
        Example:
        request.json = {"destination":"penang",
                        "dates":"August",
                        "duration":"2 days",
                        "number_of_pax":"2",
                        "filter":"foodie, attractions, magical",
                        "budget":"$2000",
                        "prompt":""}
        """
        # try:
        itinerary_payload = rag.generate_travel_itinerary(request.json, duo=True, pure_LLM=True)
        # print(itinerary_payload)
        try:
            print(itinerary_payload["response"].text)
            output = json.loads(itinerary_payload["response"].text)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error \n{e}\n occurred while generating the travel itinerary", 500  # Internal Server Error
    else:
        return "This endpoint only accepts POST requests", 405  # Method Not Allowed


@app.route('/api/mock', methods=['POST'])
def generate_package():
    if request.method == 'POST':
        bearer_token = request.headers.get('Authorization')
        print(bearer_token)
        if not bearer_token:
            return "Unauthorized", 401

        token = bearer_token.split()[1]  # Extract the actual token
        print(token)
        if not validate_token(token):
            return "Invalid token", 401
        print(request.json) 
        """
        Example:
        request.json = {"destination":"penang",
                        "dates":"August",
                        "duration":"2 days",
                        "number_of_pax":"2",
                        "filter":"foodie, attractions, magical",
                        "budget":"$2000",
                        "prompt":""}
        """
        raw_response = static_response
        return raw_response



if __name__ == '__main__':
    jwt_token = generate_token(1)
    print(f"JWT Token: {jwt_token}")  # Print the generated token
    app.run(debug=True, host='0.0.0.0')




