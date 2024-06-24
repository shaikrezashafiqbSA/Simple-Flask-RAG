EMPTY_RESPONSE = {
                    "itinerary": [
                        {
                            "activities": [
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                },
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                },
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                }
                            ],
                            "day": "",
                            "description": "",
                            "title": ""
                        },
                        {
                            "activities": [
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                },
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                },
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                }
                            ],
                            "day": "",
                            "description": "",
                            "title": ""
                        }
                    ],
                    "pricing": {
                        "total_cost": ""
                    },
                    "summary": "No destination provided. Please provide at least a destination to generate an itinerary."
                }


NULL_RESPONSE = {
                    "itinerary": [
                        {
                            "activities": [
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                },
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                },
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                }
                            ],
                            "day": "",
                            "description": "",
                            "title": ""
                        },
                        {
                            "activities": [
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                },
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                },
                                {
                                    "description": "",
                                    "inventory": "",
                                    "price": "",
                                    "time": "",
                                    "title": ""
                                }
                            ],
                            "day": "",
                            "description": "",
                            "title": ""
                        }
                    ],
                    "pricing": {
                        "total_cost": ""
                    },
                    "summary": "This destination is not supported."
                }


NULL_DESTINATION_RESPONSE =         {
                "summary": "This destination is not supported. Please provide a valid destination.",
                "country": "",
                "main_cover": "",
                "pricing": { "total_cost": "" },  # Estimated total cost
                "itinerary_id": "NAN",
                "itinerary": [
                ]
        } 

NULL_DURATION_RESPONSE =         {
                "summary": "Duration too long, keep to below <= 7 days",
                "country": "",
                "main_cover": "",
                "pricing": { "total_cost": "" },  # Estimated total cost
                "itinerary_id": "NAN",
                "itinerary": [
                ]
        } 

NULL_PAX_RESPONSE =         {
                "summary": "Number of Pax too large, keep to below <= 10 pax",
                "country": "",
                "main_cover": "",
                "pricing": { "total_cost": "" },  # Estimated total cost
                "itinerary_id": "NAN",
                "itinerary": [
                ]
        } 