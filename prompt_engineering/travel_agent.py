
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
        - Activities should be referenced from the AVAILABLE INVENTORY, or recommend alternatives based on your knowledge.
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
        * Calculate the total package cost, referencing the AVAILABLE INVENTORY. If pricing isn't available, use "unavailable" for all fields.
        'pricing': 'total_cost': 'unavailable'
"""

travel_package_inner_prompt_2 = """
        ****OUTPUT****
        IMPORTANT NOTE: The itinerary must strictly adhere to the following structure, utilizing as much inventory from AVAILABLE INVENTORY as possible:

        ***summary***
        Write an engaging one-paragraph summary containing AT LEAST 100 words to recommend the travel itinerary.
        Open with a captivating sentence highlighting how the itinerary aligns with the customer's interests (based on tags and the itinerary generated below).
        Expand on each tag, briefly describing what the destination offers related to each tag, using persuasive language.
        Also include a geographically feasible subdestination to subdestination highlights in the summary, eg: "from x to y to z to a back to x"
        
        ***country***
        "country": identify the country for the itinerary. Example: "country": "Malaysia"

        ***main_cover***
        "main_cover": field that is placeholder for the image file to be used as a cover for this entire itinerary. Example: "cover": "/malaysia/malacca/activity/tours/1.jpg"

        ***itinerary_id***
        "itinerary_id": "NAN"  # This field is a placeholder. Produce as is. 
        
        ***itinerary***
        For EACH day, provide:
        - A detailed summary (at least 100 words) outlining the day's plan, structured around morning, afternoon, and evening. (structured around breakfast, lunch, dinner)
        - Activities, accomodation should be constructed as much as possible from whatever in AVAILABLE INVENTORY LIST matching as best as possible to the CLIENT REQUIREMENTS (especially to tags), ELSE recommend better alternatives based on your knowledge that better matches the CLIENT REQUIREMENTS.
        - The AVAILABLE INVENTORY LIST is a list of inventories (from accomodation packages, to activities, to food) that can be fulfilled in the destination. It includes the following fields: "title", "Vendor ID", "Activity ID", "Type", "Tags", "Description". Where "Description" includes inventory specifications such as activity/accomodation/pricing
        - IMPORTANT: THERE MUST BE as much days as per CLIENT REQUIREMENTS.
        - IMPORTANT: THERE MUST BE morning, afternoon, and evening activities for each day.
        - The fields "Vendor ID" and "Activity ID" MUST be filled in with the corresponding inventories from the AVAILABLE INVENTORY.
        - Include a placeholder "cover" image filename for each activity. Example: "cover": "/country/destination/x1/y1.jpg" where x1 and y1 are the Vendor ID and Activity ID respectively if available. Else just put a placeholder image.
        - Limit tags to a maximum of 2 per time slot.
        - IMPORTANT: There must be at least 1 food activity and 1 places activity for each day and time slot.
        - IMPORTANT: For each food activity and places activity referenced from AVAILABLE INVENTORY, summarize as much data (in at least 3 sentences) and description as possible from the activity description.  
        - IMPORTANT: There MUST not be repeat activities in the itinerary. There must be no repeat food activities from the same place.

        ***pricing***
        * Calculate the total package cost for total pax, referencing the prices from the AVAILABLE INVENTORY else estimate from your knowledge.

     Follow this example format for the payload:
        '''
        {
                "summary": "A captivating summary of the entire itinerary (100+ words)",
                "country": "Malaysia",
                "main_cover": "/malaysia/penang/cover.jpg",
                "pricing": { "total_cost": "$500" },  # Estimated total cost
                "itinerary_id": "NAN",
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
"""

travel_package_inner_prompt_2 = """
        ****OUTPUT****
        IMPORTANT NOTE: The itinerary must strictly adhere to the following structure, utilizing as much inventory from AVAILABLE INVENTORY as possible:

        ***summary***
        Write an engaging one-paragraph summary containing AT LEAST 100 words to recommend the travel itinerary.
        Open with a captivating sentence highlighting how the itinerary aligns with the customer's interests (based on tags and the itinerary generated below).
        Expand on each tag, briefly describing what the destination offers related to each tag, using persuasive language.
        Also include a geographically feasible subdestination to subdestination highlights in the summary, eg: "from x to y to z to a back to x"
        
        ***country***
        "country": identify the country for the itinerary. Example: "country": "Malaysia"

        ***main_cover***
        "main_cover": field that is placeholder for the image file to be used as a cover for this entire itinerary. Example: "cover": "/malaysia/malacca/activity/tours/1.jpg"

        ***itinerary_id***
        "itinerary_id": "NAN"  # This field is a placeholder. Produce as is. 
        
        ***itinerary***
        For EACH day, provide:
        - A detailed summary (at least 100 words) outlining the day's plan, structured around morning, afternoon, and evening. (structured around breakfast, lunch, dinner)
        - Activities, accomodation should be constructed as much as possible from whatever in AVAILABLE INVENTORY LIST matching as best as possible to the CLIENT REQUIREMENTS (especially to tags), ELSE recommend better alternatives based on your knowledge that better matches the CLIENT REQUIREMENTS.
        - The AVAILABLE INVENTORY LIST is a list of inventories (from accomodation packages, to activities, to food) that can be fulfilled in the destination. It includes the following fields: "title", "Vendor ID", "Activity ID", "Type", "Tags", "Description". Where "Description" includes inventory specifications such as activity/accomodation/pricing
        - IMPORTANT: THERE MUST BE as much days as per CLIENT REQUIREMENTS.
        - IMPORTANT: THERE MUST BE at at least 1 morning, afternoon, and evening food, places activity for each day.
        - The fields "Vendor ID" and "Activity ID" MUST be filled in with the corresponding inventories from the AVAILABLE INVENTORY.
        - Include a placeholder "cover" image filename for each activity. Example: "cover": "/country/destination/x1/y1.jpg" where x1 and y1 are the Vendor ID and Activity ID respectively if available. Else just put a placeholder image.
        - Limit tags to a maximum of 2 per time slot.
        - IMPORTANT: There must be at least 1 food activity and 1 places activity for each day's time slot.
        - IMPORTANT: For each food activity and places activity referenced from AVAILABLE INVENTORY, summarize as much data (in at least 3 sentences) and description as possible from the activity description.  
        - IMPORTANT: There MUST not be repeat activities in the itinerary. There must be no repeat food activities from the same place.

        ***pricing***
        * Calculate the total package cost for total pax, referencing the prices from the AVAILABLE INVENTORY else estimate from your knowledge.

     Follow this example format for the payload:
        '''
        {
                "summary": "A captivating summary of the entire itinerary (100+ words)",
                "country": "Malaysia",
                "main_cover": "/malaysia/penang/cover.jpg",
                "pricing": { "total_cost": "$500" },  # Estimated total cost
                "itinerary_id": "NAN",
                "itinerary": [
                {
                        "day": 1,
                        "title": "Morning Exploration in George Town",
                        "description": "Start your day in the heart of Penang's capital...",
                        "city": "George Town",
                        "cover": "/malaysia/penang/georgetown_morning.jpg",
                        "foods": [
                        {"name": "Breakfast at Toh Soon Cafe", 
                        "description": "Enjoy a local breakfast of charcoal-toasted bread...",
                        "time": "morning",
                        "cover": "/malaysia/penang/tohsooncafe.jpg",
                        "Vendor ID": X1,
                        "Activity ID": Y1},
                        {"name": "Ais Kacang at Penang Road Famous Teochew Chendul", 
                        "description": "Cool down with a refreshing Ais Kacang...",
                        "time": "afternoon",
                        "cover": "/malaysia/penang/chendul.jpg",
                        "Vendor ID": X2,
                        "Activity ID": Y2},
                        {"name": "Legendary nasi lemak at Nasi Kandar Line Clear", 
                        "description": "This is the best night nasi lemak spot in town...",
                        "time": "evening",
                        "cover": "/malaysia/penang/nasilemaklegeng.jpg",
                        "Vendor ID": X21,
                        "Activity ID": Y21},
                        ],
                        "places": [
                        {"name": "Street Art Tour", 
                        "description": "Explore the vibrant street art scene of George Town...",
                        "time": "morning",
                        "cover": "/malaysia/penang/streetart.jpg",
                        "Vendor ID": X3,
                        "Activity ID": Y3},
                        {"name": "Cheong Fatt Tze Mansion (The Blue Mansion)", 
                        "description": "Visit this stunning 19th-century mansion...",
                        "time": "afternoon",
                        "cover": "/malaysia/penang/bluemansion.jpg",
                        "Vendor ID": X4,
                        "Activity ID": Y4},
                        {"name": "Night jungle trekking at the National Park", 
                        "description": "explore the night trails of the national park...",
                        "time": "evening",
                        "cover": "/malaysia/penang/nighttrails.jpg",
                        "Vendor ID": X5,
                        "Activity ID": Y5},
                        ],
                        "tags": ["cultural", "historical"]
                },
                {
                        "day": 2,
                        "title": "Culinary Delights in George Town",
                        "description": "In the 2nd day of your trip, continue your culinary journey...", 
                },
                {
                        "day": 3,
                        "title": "Adventure day at Batu Ferringhi",
                        "description": "As the last day of the trip, head to Batu Ferringhi...",
                }
                // ... (more day objects)
                ]
        } 
        '''
"""