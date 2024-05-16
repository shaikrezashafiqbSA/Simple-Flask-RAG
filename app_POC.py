import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from RAG.librarian import Librarian

app = Flask(__name__)
CORS(app)  

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


@app.route('/api', methods=['POST'])
def generate_package():
    if request.method == 'POST':
        print(request.json) 

        convo_package = librarian.Traveller.generate_travel_package_foundational(request.json, model_name = "gemini-pro")

        
        raw_response = convo_package["response"].text
        response = jsonify({'bot_response': raw_response})
        return response
    else:
        return "This endpoint only accepts POST requests", 405  # Method Not Allowed

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



