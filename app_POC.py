import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from specialists.traveller import Traveller 

app = Flask(__name__)
CORS(app)  


from RAG.traveller import traveller
rag = traveller()


@app.route('/api', methods=['POST'])
def generate_package():
    if request.method == 'POST':
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
        itinerary_payload = rag.generate_travel_itinerary(request.json)

#         raw_response = {'summary': 'Penang, an enchanting island off the northwest coast of Malaysia, beckons you with its captivating blend of foodie delights, fascinating attractions, and a touch of magic. Immerse yourself in the flavors of authentic street food, explore historical landmarks that whisper tales of the past, and step into a realm of illusions and wonders. Whether you seek adventure, cultural enrichment, or simply a magical escapade, Penang has something extraordinary to offer. Prepare to embark on an unforgettable 2-day journey filled with unforgettable experiences that will leave you spellbound and craving for more.',
#  'itinerary': {'day 1 summary': "Your first day in Penang will be a whirlwind of flavors and historical discoveries. Begin with a tantalizing breakfast at a local hawker center, where the aroma of freshly cooked delicacies fills the air. Then, embark on a culinary adventure as you savor the iconic street food of Penang, from aromatic char kway teow to succulent asam laksa. Afterward, delve into the city's rich past by visiting the Kek Lok Si Temple, a stunning Buddhist temple complex adorned with intricate carvings and vibrant murals. As the day progresses, explore the Clan Jetties, a charming waterfront community built on stilts, and witness the vibrant street art that transforms the city's walls into an open-air gallery. Conclude your day with a memorable dinner at a traditional nyonya restaurant, where you can indulge in the unique flavors of Peranakan cuisine.",
#   'day 1 itinerary': [{'title': 'Penang Street Food Tour',
#     'text': "Embark on a culinary adventure through the vibrant streets of George Town, where the air is filled with the tantalizing aromas of Penang's famous street food. From the savory delights of char kway teow to the tangy flavors of asam laksa, your taste buds will be in for a treat. As you explore the bustling hawker centers and street-side stalls, you'll witness the skills of local vendors who have mastered the art of creating these delectable dishes. Along the way, learn about the rich history and cultural influences that have shaped Penang's unique cuisine.",
#     'inventory': 'available! Price: $20'},
#    {'title': 'Kek Lok Si Temple',
#     'text': "Step into the awe-inspiring Kek Lok Si Temple, a magnificent Buddhist temple complex that is a true architectural marvel. As you wander through its vast halls and courtyards, admire the intricate carvings, vibrant murals, and towering pagodas that adorn every corner. Learn about the temple's fascinating history and the beliefs and practices of the Buddhist community that calls it home. Don't miss the opportunity to climb to the top of the temple for breathtaking panoramic views of Penang.",
#     'inventory': 'unavailable! Price: $10'},
#    {'title': 'Clan Jetties',
#     'text': 'Venture to the Clan Jetties, a charming waterfront community built on stilts over the sea. Stroll along the wooden walkways and marvel at the colorful houses and vibrant street art that line the narrow alleyways. Learn about the unique history and culture of this community, which has been home to Chinese immigrants for generations. As you explore, take in the picturesque views of the sea and the bustling harbor beyond.',
#     'inventory': 'available! Price: $5'},
#    {'title': 'Street Art Exploration',
#     'text': "Discover the vibrant street art that transforms the walls of George Town into an open-air gallery. As you wander through the city's streets and alleys, you'll encounter a diverse collection of murals, from whimsical and colorful designs to thought-provoking and politically charged pieces. Learn about the talented local and international artists who have contributed to this vibrant art scene, and capture some Insta-worthy shots against these eye-catching backdrops.",
#     'inventory': 'unavailable! Price: $5'},
#    {'title': 'Nyonya Dinner',
#     'text': 'Indulge in the unique flavors of Peranakan cuisine at a traditional nyonya restaurant. This hybrid cuisine, which blends Chinese and Malay influences, offers a tantalizing array of dishes that are sure to delight your taste buds. From the aromatic rendang to the tangy assam pedas, each dish is a testament to the culinary skills of the Peranakan community. As you savor your meal, learn about the history and traditions that have shaped this vibrant cuisine.',
#     'inventory': 'unavailable! Price: $25'}],
#   'day 2 summary': "Your second day in Penang will be filled with magical illusions, historical encounters, and a touch of nature's beauty. Immerse yourself in the world of optical illusions and interactive exhibits at the Trick Eye Museum, where you'll have the chance to capture some hilarious and mind-boggling photos. Then, journey back in time as you explore the Penang State Museum, which houses a fascinating collection of artifacts and exhibits that narrate the rich history of Penang. For a touch of greenery, escape to the serene Penang Botanic Gardens, where you can wander among lush tropical plants and admire the vibrant colors of nature. Conclude your day with a memorable dinner at a rooftop restaurant, where you can savor delicious food while enjoying stunning panoramic views of the city.",
#   'day 2 itinerary': [{'title': 'Trick Eye Museum',
#     'text': "Step into a world of optical illusions and interactive exhibits at the Trick Eye Museum. Prepare to be amazed as you navigate through mind-boggling displays that challenge your perception and create hilarious photo opportunities. From posing with dinosaurs to soaring through the sky, the museum offers endless possibilities for capturing unique and shareable memories. Don't miss the chance to immerse yourself in this interactive wonderland and create unforgettable moments with your loved ones.",
#     'inventory': 'available! Price: $20'},
#    {'title': 'Penang State Museum',
#     'text': "Journey back in time as you explore the Penang State Museum, a treasure trove of Penang's rich history and heritage. Wander through its galleries and discover fascinating artifacts, exhibits, and interactive displays that narrate the island's captivating story. From ancient artifacts to colonial relics, the museum provides a glimpse into the diverse cultural influences that have shaped Penang over the centuries. Don't miss the opportunity to delve into the island's past and gain a deeper appreciation for its present.",
#     'inventory': 'available! Price: $10'},
#    {'title': 'Penang Botanic Gardens',
#     'text': "Escape to the serene Penang Botanic Gardens, a haven of lush tropical plants and vibrant colors. As you wander through the gardens, admire the beauty of towering trees, exotic flowers, and manicured lawns. Discover the diverse flora and fauna that call this natural sanctuary home, and take a moment to relax and soak in the tranquility of your surroundings. Whether you're a nature enthusiast or simply seeking a respite from the hustle and bustle of the city, the Penang Botanic Gardens offer a rejuvenating and inspiring experience.",
#     'inventory': 'unavailable! Price: $5'},
#    {'title': 'Rooftop Dinner',
#     'text': "Conclude your day in Penang with a memorable dinner at a rooftop restaurant. As you savor delicious cuisine, enjoy stunning panoramic views of the city. Watch the sunset paint the sky in vibrant hues, and admire the twinkling lights of the cityscape as night falls. Whether you're celebrating a special occasion or simply seeking a romantic and unforgettable dining experience, a rooftop dinner in Penang is sure to leave a lasting impression.",
#     'inventory': 'unavailable! Price: $30'}]},
#  'pricing': {'total_cost': '$350',
#   'per_day_cost': '$175',
#   'per_activity_cost': '$20-$30'}}
        
        output = json.loads(itinerary_payload["response"].text)
        return output
    else:
        return "This endpoint only accepts POST requests", 405  # Method Not Allowed

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



