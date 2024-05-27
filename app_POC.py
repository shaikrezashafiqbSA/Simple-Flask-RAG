import json
import datetime
from flask import Flask, request, jsonify
import jwt
from flask_cors import CORS

from RAG.traveller import traveller


app = Flask(__name__)
CORS(app)  



rag = traveller()

def generate_token(user_id):
    secret_key = "12345"  
    payload = {"user_id": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)}
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def validate_token(token):
    try:
        secret_key = "12345"  # Replace with your actual secret key
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = payload.get("user_id")
        # Validate user_id or any other relevant checks
        return True
    except jwt.ExpiredSignatureError:
        return False
    
@app.route('/api', methods=['POST'])
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
        try:
            print("Generating travel itinerary...")
            itinerary_payload = rag.generate_travel_itinerary(request.json)
            print(itinerary_payload)
            output = json.loads(itinerary_payload["response"].text)
            return output
        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error \n{e}\n occurred while generating the travel itinerary", 500  # Internal Server Error
    else:
        return "This endpoint only accepts POST requests", 405  # Method Not Allowed
    
@app.route('/api_mock', methods=['POST'])
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
        raw_response = {'summary': "Escape to the enchanting island of Penang, a foodie's paradise with a touch of magic and a wealth of attractions! Immerse yourselves in Penang's vibrant culinary scene, tantalizing your taste buds with diverse flavors. Explore captivating attractions, from historical landmarks to modern wonders. Experience the island's magical aura at enchanting museums, where illusions and wonder await.",
                'itinerary': {'day1_summary': "Welcome to Penang, Malaysia! Kickstart your adventure with a hearty breakfast before immersing yourselves in the magical world of Ghost Museum. After lunch, ascend to new heights at The Top Penang, marveling at breathtaking views. Indulge in a delightful dinner at De' 8000 Mini Golf Cafe, where you can enjoy a round of mini-golf.",
                'day1_itinerary': [{'title': 'Ghost Museum',
                    'text': "Step into a realm of spine-tingling encounters at Ghost Museum, Penang's spooktacular attraction! Explore three floors of meticulously crafted exhibits, each featuring hauntingly realistic scenes and spooky characters. Get ready for some fun photo opportunities with free costumes and props, and let the knowledgeable guides lead you through the history of ghosts from around the world.",
                    'inventory': 'available',
                    'price': 36},
                {'title': 'The Top Penang',
                    'text': "Prepare for breathtaking panoramic views of Penang Island from The Top Penang! Ascend to the observation deck for a bird's-eye perspective of the island's cityscape, rolling hills, and sparkling coastline. Take a thrilling stroll on the Rainbow Skywalk, a glass-bottomed platform that will test your courage and reward you with unforgettable memories. Don't miss the other exciting attractions within The Top, including the Jurassic Research Centre and the 4D Adventure.",
                    'inventory': 'available',
                    'price': 132},
                {'title': "De' 8000 Mini Golf Cafe",
                    'text': "Unwind and enjoy a delightful dining experience at De' 8000 Mini Golf Cafe. Putt your way through their 18-hole mini golf course, challenging your companion to a friendly competition. Afterward, indulge in a delectable spread of halal food and refreshing beverages. From local favorites to international delights, their menu caters to diverse palates. ",
                    'inventory': 'available',
                    'price': 'unavailable'}],
                'day2_summary': "On your second day in Penang, start with a delightful breakfast before embarking on a journey into a world of illusions at Magic World Penang. Enjoy lunch at a local eatery, savoring Penang's culinary delights. Afterward, retreat to your comfortable accommodation at Raia Inn Penang, where you can relax and rejuvenate before bidding farewell to this captivating island.",
                'day2_itinerary': [{'title': 'Magic World Penang',
                    'text': 'Get ready for a day filled with optical illusions and interactive experiences at Magic World Penang. Step into a world of wonder as you explore their various zones, including the 3D Upside Down Museum, 3D Glow Museum, and the Jurassic Alive Interactive Dinosaur Museum. Capture mind-bending photos and let your imagination run wild in this whimsical attraction.',
                    'inventory': 'available',
                    'price': 'unavailable'},
                {'title': 'Local Eatery for Lunch',
                    'text': "Penang is renowned for its diverse culinary scene, so for lunch, embark on a flavorful adventure at one of the island's many local eateries. From hawker stalls to charming cafes, you'll find an array of options serving up mouthwatering dishes. Indulge in Penang's signature dishes such as Char Kway Teow, Assam Laksa, or Nasi Kandar, each bursting with unique flavors and aromas.",
                    'inventory': 'unavailable',
                    'price': 'unavailable'},
                {'title': 'Raia Inn Penang',
                    'text': 'After a day of exploration, retreat to the comfort of Raia Inn Penang, your home away from home. Unwind in your spacious room, perfect for families or couples seeking a relaxing stay. Take a refreshing dip in the new splash pool or simply unwind and share highlights of your Penang adventure.',
                    'inventory': 'available',
                    'price': 316}],
                'pricing': {'total_cost': 'unavailable',
                'per_day_cost': 'unavailable',
                'per_activity_cost': 'unavailable'}}}
        return raw_response

if __name__ == '__main__':
    jwt_token = generate_token(1)
    print(f"JWT Token: {jwt_token}")  # Print the generated token
    app.run(debug=True, host='0.0.0.0')




