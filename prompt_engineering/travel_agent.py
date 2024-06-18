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
        - For EACH activity in the itinerary , provide a vivid, persuasive description (at least 100 words).
        - IMPORTANT: ensure that there is at least 1 foods and places activities for each day and time slot.
        - IMPORTANT: ensure that there are morning, afternoon, evening activities for each day.
        - Include pricing and availability for each activity (use "NA" if not in inventory but provide estimations if you are able to for price).
        - The fields "Vendor ID" and "Activity ID" should be filled in with the corresponding values from the Available Inventory.
        - Include a placeholder "cover" image filename for each activity. Example: "cover": "/country/destination/x1/y1.jpg" where x1 and y1 are the Vendor ID and Activity ID respectively if available. else just put a placeholder image.
        - the activities array should have at least 3 activities per day. and each day should have a morning, afternoon, and evening activity.

        Follow this FORMAT for the itinerary section:
        '''
        obj1
        "day": "1",
        "time": "morning",
        "title": "Adventure and Relaxation",
        "description": "Welcome to Aceh, Indonesia!... (Detailed 100+ word vivid walkthrough of key highlights of the day)",
        "city": "Lampuuk Beach",
        "cover": "Lampuuk.jpg",
        "tags": ["adventure"],
        "activity": [
        "title": "Lampuuk Beach Restaurant", "description": "...(Detailed 100+ word vivid description of the food activity)", "Vendor ID": "x1","Activity ID":"y1" "price": "$50", "cover": "/country/destination/x1/y1.jpg"
        ]
        ,
        obj2
        "day": "2",
        "time": "afternoon",
        "title": "Cultural Exploration",
        "description": "On the 2nd day of your trip for the afternoon... (Detailed 100+ word vivid walkthrough of key highlights of the day)",
        "city": "Aceh outskirts",
        "cover": "Aceh.jpg",
        "tags": ["foodie", "exciting", "magical"],
        "activity": [
        "title": "...", "description": "...", "Vendor ID": "x2","Activity ID":"y2" "price": "$32", "cover": "/country/destination/x2/y2.jpg"
        ]
        ,
        objn
        "day": "n",
        "time": "evening",
        "title": "Cultural Exploration",
        "description": "On the N'th day of your trip for the afternoon... (Detailed 100+ word vivid walkthrough of key highlights of the day)",
        "city": "Aceh outskirts",
        "cover": "Aceh.jpg",
        "tags": ["foodie", "exciting", "magical"],
        "activity": [
        "title": "...", "description": "...", "Vendor ID": "x5","Activity ID":"y5" "price": "$32", "cover": "/country/destination/x5/y5.jpg"
        ]
        '''

        ***pricing***
        * Calculate the total package cost for total pax, referencing the Available Inventory else sum from the constituent activities and estimate from your knowledge.
"""


# travel_package_inner_prompt = """
#         ****OUTPUT****
#         IMPORTANT NOTE: The itinerary must strictly adhere to the following structure:

#         ***summary***
#         Write an engaging one-paragraph summary containing AT LEAST 100 words to recommend the travel itinerary.
#         Open with a captivating sentence highlighting how the itinerary aligns with the traveler's interests (based on tags and the itinerary generated below).
        
#         ***cover***
#         "cover": field that is placeholder for the image file to be used as a cover for this entire itinerary. Example: "cover": "/malaysia/malacca/activity/tours/1.jpg"

#         ***itinerary***
#         For EACH day, provide:
#         - A detailed summary (at least 100 words) outlining the day's plan, structured around morning, afternoon, and evening. (structured around breakfast, lunch, dinner)
#         - Activities should be referenced from the Available Inventory, or recommend alternatives based on your knowledge.
#         - There should not be repeat activities in the itinerary.
#         - For EACH activity in the itinerary , provide a vivid, persuasive description (at least 100 words).
#         - IMPORTANT: ensure that there is at least 1 foods and places activities for each day and time slot.
#         - IMPORTANT: ensure that there are morning, afternoon, evening activities for each day.
#         - Include pricing and availability for each activity (use "NA" if not in inventory but provide estimations if you are able to for price).
#         - The fields "Vendor ID" and "Activity ID" should be filled in with the corresponding values from the Available Inventory.
#         - Include a placeholder "cover" image filename for each activity. Example: "cover": "/country/destination/x1/y1.jpg" where x1 and y1 are the Vendor ID and Activity ID respectively if available. else just put a placeholder url.
#         - the activities array should have at least 3 activities per day. and each day should have a morning, afternoon, and evening activity.

#         ***pricing***
#         * Calculate the total package cost for total pax, referencing the Available Inventory else sum from the constituent activities and estimate from your knowledge.
# """

# =============================================================================
# old travel agent
# =============================================================================

# travel_package_inner_prompt = """
#         ****OUTPUT****
#         IMPORTANT NOTE: The itinerary must strictly adhere to the following structure:

#         ***title***
#         "title": "Travel Itinerary for Aceh, Indonesia"

#         ***cover***
#         "cover": "aceh.jpg"

#         ***summary***
#         Write an engaging one-paragraph summary containing AT LEAST 200 words to recommend the travel itinerary.
#         Open with a captivating sentence highlighting how the itinerary aligns with the traveler's interests (based on tags and the itinerary generated below).
#         Expand on each tag, briefly describing what the destination offers related to each tag, using persuasive language.

#         ***itinerary***
#         For EACH day, provide:
#         - A detailed summary (at least 100 words) outlining the day's plan, structured around morning, afternoon, and evening. (structured around breakfast, lunch, dinner) 
#         - Activities should be referenced from the Available Inventory, or recommend specific alternatives (with Vendor ID: address, and Activity ID: title of activity) based on your knowledge.
#         - For EACH activity, provide a vivid, persuasive description (at least 200 words).
#         - The fields "Vendor ID" and "Activity ID" should be filled in with the corresponding values from the Available Inventory else use your own knowledge and provide a name and address.
#         - Include a "cover" for each activity. Example: "cover": "x1/y1.jpg" where x1 and y1 are the Vendor ID and Activity ID respectively.
#         - 
#         - Include pricing and availability for each activity (estimate based on your own knowledge if not in inventory).

#         Follow this FORMAT for the itinerary section:
#         '''
        
#         "day": "1",
#         "title": "Adventure and Relaxation",
#         "description": "Welcome to Aceh, Indonesia!... (Detailed 200+ word specific, vivid walkthrough of key highlights of the day)"
#         "activities": [
#             "time": "morning", "title": "Lampuuk Beach", "description": "...(Detailed 200+ word accurate walkthrough of the activity)", "Vendor ID": "x1","Activity ID":"y1" "price": "$12", "cover": "x1/y1.jpg"
#             "time": "afternoon", "title": "...", "description": "...", "price": "...", "Vendor ID": "x4","Activity ID":"y4" "price": "$32", "cover": "x4/y4.jpg"
#             "time": "evening", "title": "...", "description": "...", "price": "...", "Vendor ID": "x7","Activity ID":"y7" "price": "$3", "cover": "x7/y7.jpg"
#             ]
#         ,
#         "day": "n",
#         "title": "Cultural Exploration",
#         "description": "On the nth day of your trip... (Detailed 200+ word specific, vivid walkthrough of key highlights of the day)"
#         "activities": [
#             "time": "morning", "title":"Alue Naga Beach","description": "...(Detailed 200+ word accurate walkthrough of the activity)", "Vendor ID": "x2","Activity ID":"y2" "price": "$50", "cover": "x2/y2.jpg"
#             "time": "afternoon", "title": "...", "description": "...", "price": "...", "Vendor ID": "x3","Activity ID":"x3" "price": "$50", "cover": "x3/y3.jpg"
#             "time": "evening", "title": "...", "description": "...", "price": "...", "Vendor ID": "x8","Activity ID":"y8" "price": "$213", "cover": "x8/y8.jpg"
#             ]
#         '''

#         ***pricing***
#         * Calculate the total package cost, referencing the Available Inventory. If pricing isn't available, use your own knowledge to estimate
#         'pricing': 'total_cost': MYR'xxx'"""