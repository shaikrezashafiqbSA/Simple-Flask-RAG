


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
                "type": "integer", 
                "description": "The duration in days of the trip (e.g., 7)." 
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
                },
                "customer_id": { 
                "type": "string", 
                "description": "customer if provided, else NAN" 
                }
            },
            "required": ["destination", "dates", "duration", "number_of_pax", "filter", "budget", "customer_id"]
            }



travel_jsonSchema_1 = {
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
                                    "inventory": {"type": "string"},
                                    "price": {"type": "string"} 
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
                    "per_day_cost": {"type": "string"},
                    "per_activity_cost": {"type": "string"}
                }
            }
        },
        "required": ["summary", "itinerary", "pricing"] 
    }

travel_jsonSchema_2 = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"}, 
        "country": {"type": "string"},
        "main_cover": {"type": "string"},
        "itinerary_id": "NAN",
        "itinerary": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "day": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "time": {"type": "string"},        # Moved "time" here
                    "city": {"type": "string"},        # Added "city"
                    "cover": {"type": "string"},       # Moved "cover" here
                    "foods": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "cover": {"type": "string"},
                                "Vendor ID": {"type": "string"},
                                "Activity ID": {"type": "string"}
                            },
                            "required": ["name", "description", "cover"]
                        },
                        "maxItems": 2                   # Limit to 2 items
                    },
                    "places": {                        # Added "places"
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "cover": {"type": "string"},
                                "Vendor ID": {"type": "string"},
                                "Activity ID": {"type": "string"}
                            },
                            "required": ["name", "description", "cover"]
                        },
                        "maxItems": 2                   # Limit to 2 items
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 2                   # Limit to 2 items
                    },
                },
                "required": ["day", "title", "description", "time", "city", "cover", "foods", "places","tags"] 
            }
        },
        "pricing": {
            "type": "object",
            "properties": {
                "total_cost": {"type": "string"}
            }
        },
    },
    "required": ["summary", "country", "main_cover", "itinerary","pricing"] # Added "prompt"
}

travel_jsonSchema_null_duration = {
    "type": "object",
    "properties": {
        "summary": "Number of days > 7. Please select a shorter duration for LLM stability",
        "country": "NAN",
        "main_cover": "NAN",
        "itinerary_id": "NAN",
        "itinerary": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "day": "NAN",
                    "title": "NAN",
                    "description": "NAN",
                    "time": "NAN",          # Moved "time" here
                    "city": "NAN",          # Added "city"
                    "cover": "NAN",         # Moved "cover" here
                    "foods": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": "NAN",
                                "description": "NAN",
                                "cover": "NAN",
                                "Vendor ID": "NAN",
                                "Activity ID": "NAN"
                            },
                            "required": ["name", "description", "cover"]
                        },
                        "maxItems": 2         # Limit to 2 items
                    },
                    "places": {              # Added "places"
                        "type": "array",
                        "items": {
                            "type": "object",  # Removed extra "items"
                            "properties": {
                                "name": "NAN",
                                "description": "NAN",
                                "cover": "NAN",
                                "Vendor ID": "NAN",
                                "Activity ID": "NAN"
                            },
                            "required": ["name", "description", "cover"]
                        },
                        "maxItems": 2         # Limit to 2 items
                    },
                    "tags": {
                        "type": "array",
                        "items": "NAN",    # Added "items"
                        "maxItems": 2         # Limit to 2 items
                    }
                },
                "required": ["day", "title", "description", "time", "city", "cover", "foods", "places", "tags"]
            }
        },
        "pricing": {
            "type": "object",
            "properties": {
                "total_cost": "NAN"
            }
        }
    },
    "required": ["summary", "country", "main_cover", "itinerary", "pricing"]  
}


travel_jsonSchema_null_pax = {
    "type": "object",
    "properties": {
        "summary": "Number of pax > 10. Please select a smaller number of pax",
        "country": "NAN",
        "main_cover": "NAN",
        "itinerary_id": "NAN",
        "itinerary": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "day": "NAN",
                    "title": "NAN",
                    "description": "NAN",
                    "time": "NAN",          # Moved "time" here
                    "city": "NAN",          # Added "city"
                    "cover": "NAN",         # Moved "cover" here
                    "foods": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": "NAN",
                                "description": "NAN",
                                "cover": "NAN",
                                "Vendor ID": "NAN",
                                "Activity ID": "NAN"
                            },
                            "required": ["name", "description", "cover"]
                        },
                        "maxItems": 2         # Limit to 2 items
                    },
                    "places": {              # Added "places"
                        "type": "array",
                        "items": {
                            "type": "object",  # Removed extra "items"
                            "properties": {
                                "name": "NAN",
                                "description": "NAN",
                                "cover": "NAN",
                                "Vendor ID": "NAN",
                                "Activity ID": "NAN"
                            },
                            "required": ["name", "description", "cover"]
                        },
                        "maxItems": 2         # Limit to 2 items
                    },
                    "tags": {
                        "type": "array",
                        "items": "NAN",    # Added "items"
                        "maxItems": 2         # Limit to 2 items
                    }
                },
                "required": ["day", "title", "description", "time", "city", "cover", "foods", "places", "tags"]
            }
        },
        "pricing": {
            "type": "object",
            "properties": {
                "total_cost": "NAN"
            }
        }
    },
    "required": ["summary", "country", "main_cover", "itinerary", "pricing"]  
}

travel_jsonSchema_null_destination = {
    "type": "object",
    "properties": {
        "summary": "Unsupported destination, please try another destination.",
        "country": "NAN",
        "main_cover": "NAN",
        "itinerary_id": "NAN",
        "itinerary": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "day": "NAN",
                    "title": "NAN",
                    "description": "NAN",
                    "time": "NAN",          # Moved "time" here
                    "city": "NAN",          # Added "city"
                    "cover": "NAN",         # Moved "cover" here
                    "foods": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": "NAN",
                                "description": "NAN",
                                "cover": "NAN",
                                "Vendor ID": "NAN",
                                "Activity ID": "NAN"
                            },
                            "required": ["name", "description", "cover"]
                        },
                        "maxItems": 2         # Limit to 2 items
                    },
                    "places": {              # Added "places"
                        "type": "array",
                        "items": {
                            "type": "object",  # Removed extra "items"
                            "properties": {
                                "name": "NAN",
                                "description": "NAN",
                                "cover": "NAN",
                                "Vendor ID": "NAN",
                                "Activity ID": "NAN"
                            },
                            "required": ["name", "description", "cover"]
                        },
                        "maxItems": 2         # Limit to 2 items
                    },
                    "tags": {
                        "type": "array",
                        "items": "NAN",    # Added "items"
                        "maxItems": 2         # Limit to 2 items
                    }
                },
                "required": ["day", "title", "description", "time", "city", "cover", "foods", "places", "tags"]
            }
        },
        "pricing": {
            "type": "object",
            "properties": {
                "total_cost": "NAN"
            }
        }
    },
    "required": ["summary", "country", "main_cover", "itinerary", "pricing"]  
}


travel_jsonSchema_2 = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"}, 
        "country": {"type": "string"},
        "main_cover": {"type": "string"},
        "itinerary_id": "NAN",
        "itinerary": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "day": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "city": {"type": "string"},        # Added "city"
                    "cover": {"type": "string"},       # Moved "cover" here
                    "foods": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "time": {"type": "string"},        # Moved "time" here
                                "cover": {"type": "string"},
                                "Vendor ID": {"type": "string"},
                                "Activity ID": {"type": "string"}
                            },
                            "required": ["name", "description", "time", "cover", "Vendor ID", "Activity ID"]
                        },
                        "minItems": 3                   # Limit to 2 items
                    },
                    "places": {                        # Added "places"
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "time": {"type": "string"},        # Moved "time" here
                                "cover": {"type": "string"},
                                "Vendor ID": {"type": "string"},
                                "Activity ID": {"type": "string"}
                            },
                            "required": ["name", "description", "time", "cover","Vendor ID", "Activity ID"]
                        },
                        "minItems": 3                   # Limit to 2 items
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 2                   # Limit to 2 items
                    },
                },
                "required": ["day", "title", "description", "city", "cover", "foods", "places","tags"] 
            }
        },
        "pricing": {
            "type": "object",
            "properties": {
                "total_cost": {"type": "string"}
            }
        },
    },
    "required": ["summary", "country", "main_cover", "itinerary","pricing"] # Added "prompt"
}