import json
from flask import Flask, request, jsonify
# from flask_cors import CORS
from RAG.librarian import Librarian

app = Flask(__name__)
# CORS(app, resources={r"/generate_package": {'Access-Control-Allow-Origin': "*"}})  

librarian = Librarian(librarian_LLM_model = "GEMINI")

# SELECT SPECIALIST DATABASE
librarian.select_specialist(specialist = "traveller", specialist_LLM_model = "GEMINI", )

# Ask librarian to get acquinted with the specialist database
librarian.Traveller.load_data_model(reembed = False,
                                    embed_id = 0,
                                    data_model_keys = {"TEST - CLIENT":"CLIENT ID",
                                                        "TEST - CLIENT REQUEST":"CLIENT ID",
                                                        "TEST - FLIGHTS":"FLIGHT ID",
                                                        "TEST - ACCOMODATIONS":"ACCOMODATION ID",
                                                        "TEST - ACTIVITIES":"ACTIVITY ID",
                                                        "TEST - SERVICES":"SERVICE ID",
                                                        },
                                    reembed_table = {"TEST - CLIENT":True,
                                                    "TEST - CLIENT REQUEST":True,
                                                    "TEST - FLIGHTS":True,
                                                    "TEST - ACCOMODATIONS":True,
                                                    "TEST - ACTIVITIES":True,
                                                    "TEST - SERVICES":True,
                                                    }       
                                    )

app = Flask(__name__)

@app.route('/generate_package', methods=['POST'])
def generate_package():
    print(request.json)
    # if 'message' not in request.json:
    #     return jsonify({'error': 'Missing "message" field in request'}), 400

    message = request.json
    print(message)
    """
    message should contain: 
    prompt 
    5 fields (destination, budget, duration, number of pax, dates)
    filter (optional theme: backpacker trip, halal tour, scenic view)
    if prompt is empty then the 5 fields should be used to generate a package
    if prompt is not empty then the prompt should be used to generate a package

    """


    # First check if prompt is empty, if empty then 
    convo_package = librarian.Traveller.generate_travel_package_foundational(message, model_name = "gemini-pro")


    raw_response = convo_package["response"].text
    response = jsonify({'bot_response': raw_response})

    # response.headers.add('Access-Control-Allow-Origin', '*')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization') 
    # response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS') 
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")

    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)