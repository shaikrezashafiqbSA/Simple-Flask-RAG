import json
import re
import time
import numpy as np
import datetime
from flask import Flask, request, jsonify, Response, stream_with_context
import jwt
from flask_cors import CORS
from settings import CREDENTIALS_FILE, SHEET_NAME, WORKSHEET_NAME, BEARER_TOKEN_SECRET_KEY, WORKSHEET_PROMPTS_NAME

from RAG.traveller import traveller
from responses.static import static_response
from gdrive.gdrive_handler import GspreadHandler

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
    secret_key = BEARER_TOKEN_SECRET_KEY  
    payload = {"user_id": user_id} #, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def validate_token(token):
    try:
        secret_key = BEARER_TOKEN_SECRET_KEY 
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

@app.route('/api/3', methods=['POST'])
def generate_package_from_model_V3():
    """
    Stream output
    """
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
        message, query = rag.generate_travel_itinerary(request.json, stream=True)
        print(request.json)


        model = rag.model
        # print(itinerary_payload)

        try:
    
            top_inventories = None
            timestamp_id = time.time_ns()
            customer_id = message.get("customer_id", "NAN")
            def generate():
                    summary_match_flag = True
                    country_match_flag = True
                    cover_match_flag = True
                    itinerary_id_match_flag = True
                    stream_response = model.generate_content(query, stream=True)
                    buffer = ""
                    all_content = ""
                    t0 = time.time()
                    for chunk in stream_response:
                        chunk_text = chunk.text

                        # Append to the buffer
                        all_content += chunk_text
                        buffer += chunk_text
                        try:
                            # print(f"buffer: {buffer}\n")
                            # Try to load the buffer as JSON
                            data = json.loads(buffer)
                            # Clear the buffer if loading was successful
                            buffer = ""

                            # Yield sections in the desired order
                            if 'summary' in data and not data.get('yield_summary', False):
                                print(f"Yielding summary: {data['summary']}")
                                yield json.dumps({'summary': data['summary']}) + "\n"
                                data['yield_summary'] = True  # Mark summary as yielded
                            if 'pricing' in data and not data.get('yield_pricing', False):
                                print(f"Yielding pricing: {data['pricing']}")
                                yield json.dumps({'pricing': data['pricing']}) + "\n"
                                data['yield_pricing'] = True  # Mark pricing as yielded

                            # Yield 'country' and 'cover' sections if they exist and haven't been yielded
                            for key in ['country', 'cover']:
                                if key in data and not data.get(f'yield_{key}', False):
                                    print(f"Yielding {key}: {data[key]}")
                                    yield json.dumps({key: data[key]}) + "\n"
                                    data[f'yield_{key}'] = True
                            if 'itinerary_id' in data and not data.get('yield_itinerary_id', False):
                                print(f"Yielding itinerary_id: {str(timestamp_id)}")
                                yield json.dumps({'itinerary_id': str(timestamp_id)}) + "\n"
                                data['yield_itinerary_id'] = True  

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
                            # Refined regex for summary
                            if summary_match_flag:
                                summary_match = re.search(r'"summary"\s*:\s*"([^"]*)"', buffer, re.DOTALL)
                                if summary_match:
                                    summary_data = summary_match.group(1)
                                    yield json.dumps({'summary': summary_data}) + '\n'
                                    print(f"!!!! YIELDED summary:\n{summary_data}\n")
                                    buffer = buffer[summary_match.end():]  # Remove summary from buffer 
                                    summary_match_flag = False
                            # # Refined regex for country
                            if country_match_flag:
                                country_match = re.search(r'"country"\s*:\s*"([^"]*)"', buffer, re.DOTALL)
                                if country_match:
                                    country_data = country_match.group(1)
                                    yield json.dumps({'country': country_data}) + '\n'
                                    print(f"!!!! YIELDED Country: \n{country_data}\n")
                                    buffer = buffer[country_match.end():]
                                    country_match_flag = False

                            # Refined regex for cover
                            if cover_match_flag:
                                cover_match = re.search(r'"main_cover"\s*:\s*"([^"]*\.jpg)"', buffer, re.DOTALL)  
                                if cover_match:
                                    cover_data = cover_match.group(1)
                                    yield json.dumps({'main_cover': cover_data}) + '\n'
                                    # buffer = buffer[cover_match.end():]  # Remove cover from buffer 
                                    print(f"!!!! YIELDED main_cover:\n{cover_data}\n")
                                    buffer = buffer[cover_match.end():]  # Remove cover from buffer
                                    cover_match_flag = False

                            # refined regex for itinerary_id
                            if itinerary_id_match_flag:
                                itinerary_id_match = re.search(r'"itinerary_id"\s*:\s*"([^"]*)"', buffer, re.DOTALL)
                                if itinerary_id_match:
                                    yield json.dumps({'itinerary_id': str(timestamp_id)}) + '\n'
                                    print(f"!!!! YIELDED itinerary_id:\n{itinerary_id_match.group(1)}\n")
                                    buffer = buffer[itinerary_id_match.end():]
                                    itinerary_id_match_flag = False

                            # If not valid JSON, try to find complete itinerary items
                            for match in re.finditer(r'({"day":\s*\d+,.+?"tags":\s*\[[^\]]+\]})', buffer, re.DOTALL):
                                payload = match.group(1)
                                yield json.dumps({'itinerary': json.loads(payload)}) + "\n"
                                print(f"!!!! Yielded itinerary item:\n{payload}\n")
                                # Remove the yielded itinerary item from the buffer
                                buffer = buffer.replace(match.group(1), '', 1)

                            # refined regex for pricing
                            pricing_match = re.search(r'"pricing"\s*:\s*({.+?})', buffer, re.DOTALL)  
                            if pricing_match:
                                pricing_data = json.loads(pricing_match.group(1))
                                yield json.dumps({'pricing': pricing_data}) + '\n'
                                print(f"!!!!\n\nYIELDED pricing: {pricing_data}\n\n")
                                buffer = buffer[pricing_match.end():]

                            continue
                    # Handle remaining buffer after the generation loop is complete
                    if buffer:
                        # Attempt to parse and yield the remaining buffer if it has pricing
                        if '"pricing":' in buffer:
                            try:
                                data = json.loads(buffer)
                                yield json.dumps({'pricing': data['pricing']}) + '\n'
                                print(f"!!!!\n\nYIELDED (buffer) pricing: {pricing_data}\n\n")
                            except json.JSONDecodeError:
                                print(f"!!!!\n\nError parsing remaining buffer: {buffer}")  
                        else: 
                            # yield the remaining buffer if it contains parts of the itinerary 
                            itinerary_matches = re.findall(r'({"day":\s*\d+,.+?"tags":\s*\[[^\]]+\]})', buffer, re.DOTALL)
                            if itinerary_matches:
                                print(f"!!!! Yielding itinerary matches buffer:\n{itinerary_id_match.group(1)}\n")
                                for match in itinerary_matches:
                                    yield json.dumps({'itinerary': json.loads(match)}) + '\n'
                            else: 
                                yield buffer #yield remaining text 
                    total_time = np.round(time.time() - t0,2)
                    print(f"\n\nEND OF RESPONSE ({total_time}s)\n\n")

                    # print(f"all_content: {all_content}")
                    corrected_json_text = rag.fix_json(all_content)
                    rag.update_google_sheet(timestamp_id, customer_id, str(message), corrected_json_text)
                    print(f"SAVED TO DB")

            # stream_response = model.generate_content(query, stream=True)
            return Response(stream_with_context(generate()), mimetype='application/json')
        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error \n{e}\n occurred while generating the travel itinerary", 500  # Internal Server Error
    else:
        return "This endpoint only accepts POST requests", 405  # Method Not Allowed
    
# ======================================================================================================================
# Get prompts table data by timestamp row
# ======================================================================================================================

@app.route('/api/get_itinerary/<timestamp>', methods=['GET'])
def get_itinerary(timestamp):
    if request.method == 'GET':
        bearer_token = request.headers.get('Authorization')
        print(bearer_token)
        if not bearer_token:
            return "Unauthorized", 401

        token = bearer_token.split()[1]  # Extract the actual token
        print(token)
        if not validate_token(token):
            return "Invalid token", 401
        print(f"timestamp---{timestamp}")
        if not isinstance(timestamp, str):
            return jsonify({"error": "Timestamp must be a string"}), 400

        try:
            # Fetch itinerary data from Google Sheet
            gspread_handler = GspreadHandler(credentials_filepath=CREDENTIALS_FILE)
            row_data = gspread_handler.get_row_by_timestamp(SHEET_NAME, WORKSHEET_PROMPTS_NAME, timestamp)

            if row_data:
                # Extract and parse the 'itinerary' JSON string
                itinerary_json_string = row_data['itinerary']
                itinerary_data = json.loads(itinerary_json_string)

                # Update the 'itinerary' field with the parsed JSON
                row_data['itinerary'] = itinerary_data
                return jsonify(row_data)
            else:
                return jsonify({"error": "Itinerary not found"}), 404

        except Exception as e:
            print(f"Error retrieving itinerary: {e}")
            return jsonify({"error": "Error retrieving itinerary"}), 500
        

from settings import GEMINI_API_KEY
from data.ingest import GoogleDriveExtractor


@app.route('/api/ingest', methods=['GET'])
def ingest():
    if request.method == 'GET':
        bearer_token = request.headers.get('Authorization')
        print(bearer_token)
        if not bearer_token:
            return "Unauthorized", 401

        token = bearer_token.split()[1]  # Extract the actual token
        print(token)
        if not validate_token(token):
            return "Invalid token", 401
        msg = request.json
        """
        msg = {
        "folder_link": "https://drive.google.com/drive/folders/1uD7SEGQ5Y2o6oXMp-s53kKnKXXsVSD-X",
        "worksheet_name":"inventory",
        "columns_to_extract": ["Title", "Description", "Location", "Price", "Duration", "Tags", "Cover", "Vendor ID", "Activity ID"]
                ""}
        """
        folder_link = msg.get("folder_link")
        folder_link = "https://drive.google.com/drive/folders/" + folder_link

        if not isinstance(folder_link, str):
            return jsonify({"error": "folder_link must be a string"}), 400
        extractor = GoogleDriveExtractor(
            credentials_file=CREDENTIALS_FILE, 
            sheet_name=SHEET_NAME,
            worksheet_name="inventory", 
            gemini_api_key=GEMINI_API_KEY 
        )

        try:
            # load folder unto the database
            extractor.run_ETL(folder_link)
            return jsonify({"message": "Ingested successfully"}), 200
        except Exception as e:
            print(f"Error ingesting: {e}")
            return jsonify({"error": f"ingesting {e}"}), 500

# ======================================================================================================================
# PURE LLM
# ======================================================================================================================
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
        itinerary_payload = rag.generate_travel_itinerary(request.json, pure_LLM=True)
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




