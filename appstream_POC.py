import json
import re
import datetime
from flask import Flask, request, jsonify, Response, stream_with_context
import jwt
from flask_cors import CORS

from settings import GEMINI_API_KEY as api_key
from RAG.traveller import traveller


app = Flask(__name__)
CORS(app)  



rag = traveller()

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
    

from settings import GEMINI_API_KEY1 as api_key

import google.generativeai as genai
from prompt_engineering.jsonSchemas import travel_jsonSchema_2
from prompt_engineering.travel_agent import travel_package_inner_prompt_2
@app.route('/generate', methods=['POST'])
def generate_content():
    block_threshold="BLOCK_NONE"

    generation_config = {"response_mime_type": "application/json",
                                    "temperature": 0.9,
                                    "top_p": 0.95,
                                    "top_k": 40,
                                    "max_output_tokens": 1000000,}
    safety_settings = [
        {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": block_threshold
        },
        {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": block_threshold
        },
        {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": block_threshold
        },
        {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": block_threshold
        },
    ]
    model_name = "gemini-1.5-flash" #"gemini-1.5-pro-latest"
    client_requirements = "i want to go to penang in august for 3 days with 2 people. i want to experience foodie, attractions, magical. my budget is $2000."
    top_inventories = None
    query = f"""You are a travel agent creating a comprehensive itinerary given client requirements and available inventory.

        ****INPUTS****
        ***Client Requirements:***
        IMPORTANT: The itinerary must strictly adhere to the client requirements: duration (number of days!), destination, tags, budget;
        {client_requirements}
        ***Available inventory:***
        {top_inventories}
        Following content outline:
        {travel_package_inner_prompt_2}
        Follow the JSON schema strictly (from the content ouline above) fill in all required fields:
        <JSONSchema>{json.dumps(travel_jsonSchema_2)}</JSONSchema>
        """
    genai.configure(api_key = api_key)

    model = genai.GenerativeModel(model_name=model_name,
                                    generation_config=generation_config,
                                    safety_settings=safety_settings)

    def generate():
        response = model.generate_content(query, stream=True)
        buffer = ""
        in_itinerary = False

        for chunk in response:
            chunk_text = chunk.text

            # Append to the buffer
            buffer += chunk_text
            print(f"chunk_text: \n{chunk_text}\n")
            try:
                # Try to load the buffer as JSON
                data = json.loads(buffer)
                # Clear the buffer if loading was successful
                buffer = ""

                # Yield sections in the desired order
                if 'summary' in data and not data.get('yield_summary', False):
                    yield json.dumps({'summary': data['summary']}) + "\n"
                    data['yield_summary'] = True  # Mark summary as yielded
                if 'pricing' in data and not data.get('yield_pricing', False):
                    yield json.dumps({'pricing': data['pricing']}) + "\n"
                    data['yield_pricing'] = True  # Mark pricing as yielded
                
                if 'itinerary' in data: 
                    for item in data['itinerary']:
                        for category in ["foods", "places"]:
                            for activity in item.get(category, []):
                                # Add these fields from the original top_inventories data
                                if top_inventories:
                                    matching_item = next((inv_item for inv_item in top_inventories if inv_item['Title'] == activity['name']), None)
                                    if matching_item:
                                        activity["Vendor ID"] = matching_item["Vendor ID"]
                                        activity["Activity ID"] = matching_item["Activity ID"]
                                        activity["cover"] = matching_item["cover"]
                        yield json.dumps({'itinerary': item}) + "\n"

            except json.JSONDecodeError:
                # If not valid JSON, try to find complete itinerary items
                for match in re.finditer(r'({"day":\s*\d+,.+?"tags":\s*\[[^\]]+\]})', buffer, re.DOTALL):
                    yield json.dumps({'itinerary': json.loads(match.group(1))}) + "\n"
                    # Remove the yielded itinerary item from the buffer
                    buffer = buffer.replace(match.group(1), '', 1)
                    
                # If not valid JSON and no complete itinerary item found, wait for more data
                continue

        # Handle remaining buffer at the end of the generation
        if buffer:
            # Attempt to parse and yield the remaining buffer if it has pricing
            if '"pricing":' in buffer:
                try:
                    data = json.loads(buffer)
                    yield json.dumps({'pricing': data['pricing']}) + "\n"
                except json.JSONDecodeError:
                    print(f"Error parsing remaining buffer: {buffer}")  
            else: 
                # yield the remaining buffer if it contains parts of the itinerary 
                itinerary_matches = re.findall(r'({"day":\s*\d+,.+?"tags":\s*\[[^\]]+\]})', buffer, re.DOTALL)
                if itinerary_matches:
                    for match in itinerary_matches:
                        yield json.dumps({'itinerary': json.loads(match)}) + '\n'
                else: 
                    yield buffer #yield remaining text 
        print(f"\n\nEND OF RESPONSE\n\n")

    return Response(stream_with_context(generate()), mimetype='application/json')






if __name__ == '__main__':
    jwt_token = generate_token(1)
    print(f"JWT Token: {jwt_token}")  # Print the generated token
    app.run(debug=True, host='0.0.0.0')