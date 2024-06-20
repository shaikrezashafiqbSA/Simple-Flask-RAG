
travel_package_inner_prompt_1 = """
        ****OUTPUT****
        IMPORTANT NOTE: The itinerary must strictly adhere to the following structure:

        ***summary***
        Write an engaging one-paragraph summary containing AT LEAST 200 words to recommend the travel itinerary.
        Open with a captivating sentence highlighting how the itinerary aligns with the traveler's interests (based on tags and the itinerary generated below).
        Expand on each tag, briefly describing what the destination offers related to each tag, using persuasive language.

        ***itinerary***
        For EACH day, provide:
        - A detailed summary (at least 200 words) outlining the day's plan, structured around morning, afternoon, and evening. (structured around breakfast, lunch, dinner) 
        - Activities should be referenced from the Available Inventory, or recommend alternatives based on your knowledge.
        - For EACH activity, provide a vivid, persuasive description (at least 200 words).
        - Include pricing and availability for each activity (use "unavailable" if not in inventory).

        Follow this FORMAT for the itinerary section:
        '''
        
        "day": "Day 1",
        "title": "Adventure and Relaxation",
        "description": "Welcome to Aceh, Indonesia!... (Detailed 200+ word vivid walkthrough of key highlights of the day)"
        "activities": [
            "time": "morning", "title": "Lampuuk Beach", "description": "...(Detailed 200+ word vivid walkthrough of the activity)", "inventory": "unavailable", "price": "estimated $40"
            "time": "afternoon", "title": "...", "description": "...", "inventory": "...", "price": "..."
            "time": "evening", "title": "...", "description": "...", "inventory": "...", "price": "..."
            ]
        ,
        "day": "Day 2",
        "title": "Cultural Exploration",
        "description": "On the nth day of your trip... (Detailed 200+ word vivid walkthrough of key highlights of the day)"
        "activities": [
            "time": "morning", "title":"Alue Naga Beach","description": "...(Detailed 200+ word vivid walkthrough of the activity)", "inventory": "vendor ID: x", "price": "$50"
            "time": "afternoon", "title": "...", "description": "...", "inventory": "...", "price": "..."
            "time": "evening", "title": "...", "description": "...", "inventory": "...", "price": "..."
            ]
        '''

        ***pricing***
        * Calculate the total package cost, referencing the Available Inventory. If pricing isn't available, use "unavailable" for all fields.
        'pricing': 'total_cost': 'unavailable'
"""

travel_package_inner_prompt_2 = """
        ****OUTPUT****
        IMPORTANT NOTE: The itinerary must strictly adhere to the following structure:

        ***summary***
        Write an engaging one-paragraph summary containing AT LEAST 100 words to recommend the travel itinerary.
        Open with a captivating sentence highlighting how the itinerary aligns with the traveler's interests (based on tags and the itinerary generated below).
        Expand on each tag, briefly describing what the destination offers related to each tag, using persuasive language.
        
        ***cover***
        "cover": field that is placeholder for the image file to be used as a cover for this entire itinerary. Example: "cover": "/malaysia/malacca/activity/tours/1.jpg"

        ***itinerary***
        For EACH day, provide:
        - A detailed summary (at least 100 words) outlining the day's plan, structured around morning, afternoon, and evening. (structured around breakfast, lunch, dinner)
        - Activities should be referenced from the Available Inventory, or recommend alternatives based on your knowledge.
        - There should not be repeat activities in the itinerary.
        - IMPORTANT: THERE MUST BE as much days as required by the user.
        - For EACH time slot (morning, afternoon, evening), include at least one food activity under "activities".
        - Include pricing and availability for each activity (use "NA" if not in inventory but provide estimations if you are able to for price).
        - The fields "Vendor ID" and "Activity ID" should be filled in with the corresponding values from the Available Inventory if available.
        - Include a placeholder "cover" image filename for each activity. Example: "cover": "/country/destination/x1/y1.jpg" where x1 and y1 are the Vendor ID and Activity ID respectively if available. Else just put a placeholder image.
        - Limit tags to a maximum of 2 per time slot.
        - IMPORTANT: There must be at least 1 food activity and 1 places activity for each day and time slot.


     Follow this example format for the itinerary section:
        '''
        {
                "summary": "A captivating summary of the entire itinerary (100+ words)",
                "pricing": { "total_cost": "$500" },  # Estimated total cost
                "country": "Malaysia",
                "main_cover": "/malaysia/penang/cover.jpg",
                "itinerary": [
                {
                        "day": 1,
                        "title": "Morning Exploration in George Town",
                        "description": "Start your day in the heart of Penang's capital...",
                        "time": "morning",
                        "city": "George Town",
                        "cover": "/malaysia/penang/georgetown_morning.jpg",
                        "foods": [
                        {"name": "Breakfast at Toh Soon Cafe", 
                        "description": "Enjoy a local breakfast of charcoal-toasted bread...",
                        "cover": "/malaysia/penang/tohsooncafe.jpg",
                        "Vendor ID": X1,
                        "Activity ID": Y1},
                        {"name": "Ais Kacang at Penang Road Famous Teochew Chendul", 
                        "description": "Cool down with a refreshing Ais Kacang...",
                        "cover": "/malaysia/penang/chendul.jpg",
                        "Vendor ID": X2,
                        "Activity ID": Y2},
                        ],
                        "places": [
                        {"name": "Street Art Tour", 
                        "description": "Explore the vibrant street art scene of George Town...",
                        "cover": "/malaysia/penang/streetart.jpg",
                        "Vendor ID": X3,
                        "Activity ID": Y3},
                        {"name": "Cheong Fatt Tze Mansion (The Blue Mansion)", 
                        "description": "Visit this stunning 19th-century mansion...",
                        "cover": "/malaysia/penang/bluemansion.jpg",
                        "Vendor ID": X4,
                        "Activity ID": Y4},
                        ],
                        "tags": ["cultural", "historical"]
                },
                {
                        "day": 1,
                        "title": "Afternoon Culinary Delights in George Town",
                        "description": "In the afternoon, continue your culinary journey...", 
                        "time": "afternoon",  // ... (and so on for afternoon and evening)
                },
                {
                        "day": 1,
                        "title": "Evening at Batu Ferringhi",
                        "description": "As the sun sets, head to Batu Ferringhi...",
                        "time": "evening",  // ... (and so on for other days)
                }
                // ... (more day objects)
                ]
        } 
        '''

        ***pricing***
        * Calculate the total package cost for total pax, referencing the Available Inventory else estimate from your knowledge.
"""
