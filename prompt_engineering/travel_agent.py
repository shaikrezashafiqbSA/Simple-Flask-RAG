travel_package_inner_prompt_duo = """
        ****OUTPUT****
        IMPORTANT NOTE: The itinerary must strictly adhere to the following structure:

        ***summary***
        Write an engaging one-paragraph summary containing AT LEAST 100 words to recommend the travel itinerary.
        Open with a captivating sentence highlighting how the itinerary aligns with the traveler's interests (based on tags and the itinerary generated below).
        Expand on each tag, briefly describing what the destination offers related to each tag, using persuasive language.
        
        ***cover***
        "cover": "<destination>.jpg" field that is placeholder for the image file to be used as a cover for this entire itinerary. Example: "cover": "penang.jpg"


        ***itinerary***
        For EACH day, provide:
        - A detailed summary (at least 100 words) outlining the day's plan, structured around morning, afternoon, and evening. (structured around breakfast, lunch, dinner)
        - Activities should be referenced from the Available Inventory, or recommend alternatives based on your knowledge.
        - There should not be repeat activities in the itinerary.
        - For EACH item in the itinerary (segregrated into activities: foods, places), provide a vivid, persuasive description (at least 100 words).
        - IMPORTANT: ensure that there is at least 1 foods and places activities for each day and time slot.
        - IMPORTANT: ensure that there are morning, afternoon, evening activities for each day.
        - Include pricing and availability for each activity (use "NA" if not in inventory but provide estimations if you are able to for price).
        - The fields "Vendor ID" and "Activity ID" should be filled in with the corresponding values from the Available Inventory.
        - Include a placeholder "cover" image filename for each activity. Example: "cover": "x1/y1.jpg" where x1 and y1 are the Vendor ID and Activity ID respectively if available. else just put a placeholder image.
    

        Follow this FORMAT for the itinerary section:
        '''
        obj 1
        "day": "1",
        "time": "morning",
        "title": "Adventure and Relaxation",
        "description": "Welcome to Aceh, Indonesia!... (Detailed 100+ word vivid walkthrough of key highlights of the day)",
        "city": "Lampuuk Beach",
        "cover": "Lampuuk.jpg",
        "tags": ["adventure"],
        "foods": [
        "title": "Lampuuk Beach Restaurant", "description": "...(Detailed 100+ word vivid description of the food activity)", "Vendor ID": "x1","Activity ID":"y1" "price": "$50", "cover": "x1/y1.jpg"
        ]
        "places": [
            "title": "Lampuuk Beach Park", "description": "...(Detailed 100+ word vivid walkthrough of the activity)", "Vendor ID": "x1","Activity ID":"y1" "price": "$50", "cover": "x1/y1.jpg"
            ]
        ,
        obj 2
        "day": "2",
        "time": "afternoon",
        "title": "Cultural Exploration",
        "description": "On the 2nd day of your trip for the afternoon... (Detailed 100+ word vivid walkthrough of key highlights of the day)",
        "city": "Aceh outskirts",
        "cover": "Aceh.jpg",
        "tags": ["foodie", "exciting", "magical"],
        "foods": [
        "title": "...", "description": "...", "Vendor ID": "x2","Activity ID":"y2" "price": "$32", "cover": "x2/y2.jpg"
        ]
        "places": [
        "title": "...", "description": "...", "Vendor ID": "x3","Activity ID":"y3" "price": "$230", "cover": "x3/y3.jpg"
        ]
        ,
        obj 30
        "day": "30",
        "time": "evening",
        "title": "Cultural Exploration",
        "description": "On the N'th day of your trip for the afternoon... (Detailed 100+ word vivid walkthrough of key highlights of the day)",
        "city": "Aceh outskirts",
        "cover": "Aceh.jpg",
        "tags": ["foodie", "exciting", "magical"],
        "foods": [
        "title": "...", "description": "...", "Vendor ID": "x5","Activity ID":"y5" "price": "$32", "cover": "x5/y5.jpg"
        ]
        "places": [
        "title": "...", "description": "...", "Vendor ID": "x4","Activity ID":"y4" "price": "$230", "cover": "x4/y4.jpg"
        ]
        '''

        ***pricing***
        * Calculate the total package cost for total pax, referencing the Available Inventory else sum from the constituent activities and estimate from your knowledge.
"""


travel_package_inner_prompt = """
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
                "cover": "/malaysia/penang/cover.jpg",
                "itinerary": [
                {
                        "day": 1,
                        "title": "Morning Exploration in George Town",
                        "description": "Start your day in the heart of Penang's capital...",
                        "time": "morning",
                        "city": "George Town",
                        "cover": "/malaysia/penang/georgetown_morning.jpg",
                        "tags": ["cultural", "historical"],
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
                        ]
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

travel_package_inner_prompt1 = """
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
                "cover": "/malaysia/penang/cover.jpg",
                "itinerary": [
                {
                        "day": 1,
                        "title": "Morning Exploration in George Town",
                        "description": "Start your day in the heart of Penang's capital...",
                        "time": "morning",
                        "city": "George Town",
                        "cover": "/malaysia/penang/georgetown_morning.jpg",
                        "tags": ["cultural", "historical"],
                        "activities": [
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
                        {"name": "Street Art Tour", 
                        "description": "Explore the vibrant street art scene of George Town...",
                        "cover": "/malaysia/penang/streetart.jpg",
                        "Vendor ID": X3,
                        "Activity ID": Y3},
                        {"name": "Cheong Fatt Tze Mansion (The Blue Mansion)", 
                        "description": "Visit this stunning 19th-century mansion...",
                        "cover": "/malaysia/penang/bluemansion.jpg",
                        "Vendor ID": X4,
                        "Activity ID": Y4}
                        ],
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
