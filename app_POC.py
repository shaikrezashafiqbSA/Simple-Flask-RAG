import json
from flask import Flask, request, jsonify

from RAG.librarian import Librarian

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
    destination
    budget
    duration
    number of pax
    dates
    """
    # if 'itinerary_buckets' in session:
    #     itinerary_buckets = session['itinerary_buckets']
    # else:
    # itinerary_buckets = librarian.Traveller.III_semantic_decomposition(message)
    # session['itinerary_buckets'] = itinerary_buckets

    convo_package = librarian.Traveller.generate_travel_package_foundational(message, model_name = "gemini-pro")


    raw_response = convo_package["response"].text
    return jsonify({'bot_response': raw_response})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
