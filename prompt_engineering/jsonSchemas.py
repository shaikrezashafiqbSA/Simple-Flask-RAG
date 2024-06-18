


intent_jsonSchema = {
            "type": "object",
            "title": "TravelDetails",
            "description": "Details about a travel plan including destination, dates, duration, number of pax, tags, and budget.",
            "properties": {
                "destination": { 
                "type": "string", 
                "description": "The destination of the trip." 
                },
                "dates": { 
                "type": "string", 
                "description": "The dates of the trip (e.g., 2024-06-01 to 2024-06-07)." 
                },
                "duration": { 
                "type": "string", 
                "description": "The duration of the trip (e.g., 7 days)." 
                },
                "number_of_pax": { 
                "type": "integer", 
                "description": "The number of people going on the trip." 
                },
                "filter": { 
                "type": "array",
                "description": "Tags describing the trip (e.g., adventure, hidden gems).",
                "items": {
                    "type": "string"
                }
                },
                "budget": { 
                "type": "string", 
                "description": "The budget for the trip." 
                }
            },
            "required": ["destination", "dates", "duration", "number_of_pax", "filter", "budget"]
            }



# travel_jsonSchema = {
#                 "title": "Travel Itinerary",
#                 "type": "object",
#                 "properties": {
#                     "prompt": {
#                         "type": "string",
#                         "description": "Prompt that user queried"
#                     },
#                     "summary": {
#                         "type": "object",
#                         "properties": {
#                             "text": {
#                                 "type": "string",
#                                 "description": "Engaging one-paragraph summary of at least 100 words"
#                             },
#                             "cover_image": {
#                                 "type": "string",
#                                 "description": "Cover image for the summary"
#                             }
#                         },
#                         "required": ["text", "cover_image"]
#                     },
#                     "pricing": {
#                         "type": "object",
#                         "properties": {
#                             "total_cost": {
#                                 "type": "string",
#                                 "description": "Total cost for the entire journey"
#                             }
#                         },
#                         "required": ["total_cost"]
#                     },
#                     "country": {
#                         "type": "string",
#                         "description": "Destination country"
#                     },
#                     "cover": {
#                         "type": "string",
#                         "description": "Image URL for the cover image"
#                     },
#                     "itinerary": {
#                         "type": "array",
#                         "items": {
#                             "type": "object",
#                             "properties": {
#                                 "day": {
#                                     "type": "string",
#                                     "description": "Day number"
#                                 },
#                                 "title": {
#                                     "type": "string",
#                                     "description": "Title of the day"
#                                 },
#                                 "description": {
#                                     "type": "string",
#                                     "description": "Detailed summary of the day's plan"
#                                 },
#                                 "activities": {
#                                     "type": "array",
#                                     "items": {
#                                         "type": "object",
#                                         "properties": {
#                                             "time": {
#                                                 "type": "string",
#                                                 "description": "Time of day (morning, afternoon, evening)"
#                                             },
#                                             "title": {
#                                                 "type": "string",
#                                                 "description": "Title of the activity"
#                                             },
#                                             "description": {
#                                                 "type": "string",
#                                                 "description": "Detailed description of the activity"
#                                             },
#                                             "Vendor ID": {
#                                                 "type": "string",
#                                                 "description": "Vendor ID for the activity"
#                                             },
#                                             "Activity ID": {
#                                                 "type": "string",
#                                                 "description": "Activity ID for the activity"
#                                             },
#                                             "price": {
#                                                 "type": "string",
#                                                 "description": "Price of the activity"
#                                             },
#                                             "cover_image": {
#                                                 "type": "string",
#                                                 "description": "Cover image URL for the activity"
#                                             }
#                                         },
#                                         "required": ["time", "title", "description", "Vendor ID", "Activity ID", "price", "cover_image"]
#                                     },
#                                     "minItems": 3
#                                 }
#                             },
#                             "required": ["day", "title", "description", "activities"]
#                         }
#                     }
#                 },
#                 "required": ["prompt", "summary", "pricing", "country", "cover", "itinerary"]
#             }


travel_jsonSchema = {
"title": "Travel Itinerary",
"type": "object",
"properties": {
    "summary": {"type": "string"},
    "itinerary": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "day": {"type": "string"},
                "time": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "cover": {"type": "string"},
                "tags": {"type": "string"},
                "area": {"type": "string"},
                "activities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "cover": {"type": "string"},
                            "Vendor ID": {"type": "string"},
                            "Activity ID": {"type": "string"},
                            "area": {"type": "string"},
                            "price": {"type": "string"} 
                        },
                        "required": ["title", "description", "Vendor ID", "Activity ID", "price", "cover"]
                    }
                }
            },
            "required": ["day", "title", "description", "activities"]
        }
    },
    "pricing": {
        "type": "object",
        "properties": {
            "total_cost": {"type": "string"},
            "per_day_cost": {"type": "string"},
            "per_activity_cost": {"type": "string"}
        }
    }
},
"required": ["summary", "itinerary", "pricing"] 
}


travel_jsonSchema_duo = {
"title": "Travel Itinerary",
"type": "object",
"properties": {
    "summary": {"type": "string"},
    "cover": {"type": "string"},
    "itinerary": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "day": {"type": "integer"},
                "time": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "cover": {"type": "string"},
                "tags": {"type": "string"},
                "area": {"type": "string"},
                "foods": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "cover": {"type": "string"},
                            "Vendor ID": {"type": "string"},
                            "Activity ID": {"type": "string"},
                            "area": {"type": "string"},
                            "price": {"type": "string"} 
                        },
                        "required": ["title", "description", "Vendor ID", "Activity ID", "price", "cover"]
                    }
                },
                "places": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "cover": {"type": "string"},
                            "Vendor ID": {"type": "string"},
                            "Activity ID": {"type": "string"},
                            "area": {"type": "string"},
                            "price": {"type": "string"} 
                        },
                        "required": ["title", "description", "Vendor ID", "Activity ID", "price", "cover"]
                    }
                }
            },
            "required": ["day", "time", "title", "description", "cover", "tags", "area","foods", "places"]
        }
    },
    "pricing": {
        "type": "object",
        "properties": {
            "total_estimated_cost": {"type": "string"},
        }
    }
},
"required": ["summary", "itinerary", "pricing"] 
}

travel_jsonSchema0 = {
"title": "Travel Itinerary",
"type": "object",
"properties": {
    "summary": {"type": "string"},
    "cover": {"type": "string"},
    "itinerary": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "day": {"type": "integer"},
                "time": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "cover": {"type": "string"},
                "tags": {"type": "string"},
                "area": {"type": "string"},
                "activity": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "cover": {"type": "string"},
                            "Vendor ID": {"type": "string"},
                            "Activity ID": {"type": "string"},
                            "area": {"type": "string"},
                            "price": {"type": "string"} 
                        },
                        "required": ["title", "description", "Vendor ID", "Activity ID", "price", "cover"]
                    }
                },
            },
            "required": ["day", "time", "title", "description", "activity"]
        }
    },
    "pricing": {
        "type": "object",
        "properties": {
            "total_estimated_cost": {"type": "string"},
        }
    }
},
"required": ["summary", "itinerary", "pricing"] 
}





jsonSchema = {
    "title": "Travel Itinerary",
    "summary": "",  # maximum 2 short paragraphs to explain entire journey
    "pricing": "",  # rough estimate of the total costs for entire journey
    "country": "",  # destination country
    "cover": "NA",  # image url for the cover image
    "itinerary": [
                {
                    "day": "",  # day number
                    "time": "",  # morning, afternoon, evening
                    "title": "",
                    "description": "",
                    "city": "",  # city or area name
                    "cover": "",  # image url for the cover image
                    "tags": "",  # keyword of the famous things (e.g. food, culture, history)
                    "foods": [
                        {
                            "name": "",
                            "description": "",
                            "Vendor ID": "",
                            "Activity ID": "",
                            "price": "",
                            "cover": ""
                        }
                    ],
                    "places": [
                        {
                            "name": "",
                            "description": "",
                            "Vendor ID": "",
                            "Activity ID": "",
                            "price": "",
                            "cover": ""
                        }
                    ]
                }
    ]
    ,"required": ["summary", "itinerary", "pricing"] 
}

# ========================================================================================================
# old working json schema
# ========================================================================================================

travel_jsonSchema = {
        "title": {"type": "string"},
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "country": {"type": "string"},
            "cover": {"type": "string"}, # image url for the cover image
            "cover": {"type": "string"},
            "itinerary": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "day": {"type": "int"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "activities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "time": {"type": "string"},
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "price": {"type": "string"}, 
                                    "Vendor ID": {"type": "string"},
                                    "Activity ID": {"type": "string"},
                                    "cover": {"type": "string"},
                                },
                                "required": ["time", "title", "description"]
                            }
                        }
                    },
                    "required": ["day", "title", "description", "activities"]
                }
            },
            "pricing": {
                "type": "object",
                "properties": {
                    "total_cost": {"type": "string"},
                }
            }
        },
        "required": ["summary", "itinerary", "pricing"] 
    }