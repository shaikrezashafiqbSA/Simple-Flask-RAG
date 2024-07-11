import re
import numpy as np
import pandas as pd
import json
import time 
from settings import GEMINI_API_KEY1 as GEMINI_API_KEY
from settings import CREDENTIALS_FILE, SHEET_NAME, WORKSHEET_NAME
import google.generativeai as genai
from gdrive.gdrive_handler import GspreadHandler
from utils.pickle_helper import pickle_this

from prompt_engineering.jsonSchemas import intent_jsonSchema,intent_jsonSchema_multi_dest, travel_jsonSchema_1, travel_jsonSchema_2, travel_jsonSchema_null_duration, travel_jsonSchema_null_pax, travel_jsonSchema_null_destination
from prompt_engineering.responses import NULL_PAX_RESPONSE, NULL_DURATION_RESPONSE, NULL_DESTINATION_RESPONSE
from prompt_engineering.travel_agent import travel_package_inner_prompt_1, travel_package_inner_prompt_2


class EmptyResponse:
    def __init__(self, text):
        self.text = text


class traveller:
    def __init__(self,
                 generation_config = None,
                 block_threshold="BLOCK_NONE", ):
        self.GEMINI_API_KEY = GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash" 

        if generation_config is None:
            self.generation_config = {"response_mime_type": "application/json",
                                        "temperature": 0.9,
                                        "top_p": 0.95,
                                        "top_k": 40,
                                        "max_output_tokens": 1000000,}
        self.safety_settings = [
            {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": block_threshold
            },
            {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": block_threshold
            },
            {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": block_threshold
            },
            {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": block_threshold
            },
        ]

    def build_model(self, model_name, api_key):
        genai.configure(api_key = api_key)

        model = genai.GenerativeModel(model_name=model_name,
                                        generation_config=self.generation_config,
                                        safety_settings=self.safety_settings)
        
        return model
    def count_tokens(self, model, text):
        return model.count_tokens(text)
    
    def prompt(self, model, query, stream=False):
        response = model.generate_content(query, stream=stream)
        # print(response.text)
        return response

    def get_df(self, sheet_name, worksheet_name):
        gspread_handler = GspreadHandler(credentials_filepath=CREDENTIALS_FILE)
        df = gspread_handler.get_sheet_as_df(sheet_name=sheet_name, worksheet_name=worksheet_name)
        return df
    
    def clean_location_column(self, df):
        # Clean the 'Location' column
        df['Location'] = df['Location'].str.strip().str.title()
        return df

    def update_google_sheet(self, timestamp, customer_id, prompt, itinerary):
        gspread_handler = GspreadHandler(credentials_filepath=CREDENTIALS_FILE)
        """Updates the Google Sheet with the extracted text."""
        data = [{"itinerary_id":str(timestamp)+'x', "customer_id":customer_id, "prompt": prompt, "itinerary": itinerary}]
        df = pd.DataFrame(data)
        print("Updating Google Sheet...with:\n", df)
        # replace with the correct sheet name 
        gspread_handler.update_cols(df, SHEET_NAME, "prompts") #replace with the correct sheet name 

    def filter_destinations(self, destination_query, df, columns_to_embed=["Country", "Location"], return_df = False, column_title="Title", top_N=5):

        df = self.clean_location_column(df)

        # # combine the columns to embed
        df['destination'] = df[columns_to_embed].apply(lambda row: ' '.join([str(x) for x in row]), axis=1)
        # Create a regex pattern to find the query anywhere in the destination string (case-insensitive)
        pattern = re.compile(re.escape(destination_query), re.IGNORECASE)

        # Filter the DataFrame based on regex matches in the specified column
        filtered_df = df[df['destination'].astype(str).str.contains(pattern)]
        # drop destination column
        filtered_df = filtered_df.drop(columns=['destination'])
        filtered_df = filtered_df[["Title", "Vendor ID", "Activity ID","Type", "Tags", "Description"]]
        # drop duplicates by title
        filtered_df = filtered_df.drop_duplicates(subset=[column_title])
        
        return filtered_df
    
    def filter_destinations(self, destination_queries, df, columns_to_embed=["Country", "Location"], return_df = False, column_title="Title", top_N=5):
        df = self.clean_location_column(df)

        # Combine columns to embed for efficient search
        df['destination'] = df[columns_to_embed].apply(lambda row: ' '.join([str(x) for x in row]), axis=1)

        # Create a combined regex pattern for all destinations
        pattern = '|'.join([re.escape(dest) for dest in destination_queries])
        pattern = re.compile(pattern, re.IGNORECASE)  # Case-insensitive matching

        # Filter the DataFrame based on the combined pattern
        filtered_df = df[df['destination'].astype(str).str.contains(pattern)]

        # Drop the temporary 'destination' column and select desired columns
        filtered_df = filtered_df.drop(columns=['destination'])
        filtered_df = filtered_df[["Title", "Vendor ID", "Activity ID", "Type", "Tags", "Description"]]

        # Drop duplicates based on the specified column title
        filtered_df = filtered_df.drop_duplicates(subset=[column_title])

        return filtered_df
    
    def filter_by_tags(self, tags_query, df, columns_to_embed=["Type","Tags", "Title"]):
        # combine the columns to embed
        df['tags'] = df[columns_to_embed].apply(lambda row: ' '.join([str(x) for x in row]), axis=1)
        # Create a regex pattern to find the query anywhere in the destination string (case-insensitive)
        pattern = re.compile(re.escape(tags_query), re.IGNORECASE)

        pass
    
    def prompt_intent_classifier(self, message):
        """
        Example prompt: "i want to go to perlis for a hidden gems trip"
        will extract out destination, dates, duration, number_of_pax, tags, budget if available

        """
        user_intent_prompt = f"""You are a travel assistant. A user wants to go on a trip. 
        Extract the following details if available: destination, dates, duration, number_of_pax, tags, budget, customer_id. 
        If a detail is not mentioned, leave it as 'NAN'.
        If duration is NAN, assume it is a 3-day trip for 1 person.
        IMPORTANT: If the destination is fictional or nonsensical, return 'NAN' for destination.
        <User Input>:
        {message}
        Follow the JSON schema strictly and fill in all required fields.
        <JSONSchema>{json.dumps(intent_jsonSchema)}</JSONSchema>
        """

        user_intent_prompt = f"""You are a travel assistant. A user wants to go on a trip. 
        Extract the following details if available: destination, dates, duration, number_of_pax, tags, budget, customer_id. 
        destination could either be a single destination or multiple destinations, e.g.; "I want to go to Paris and then to London"
        If a detail is not mentioned, leave it as 'NAN'.
        If duration is NAN, assume it is a 3-day trip for 1 person.
        IMPORTANT: If the destination is fictional or nonsensical, return 'NAN' for destination.
        <User Input>:
        {message}
        Follow the JSON schema strictly and fill in all required fields.
        <JSONSchema>{json.dumps(intent_jsonSchema_multi_dest)}</JSONSchema>
        """
        model = self.build_model(self.model_name, api_key=self.GEMINI_API_KEY) 
        response = self.prompt(model, user_intent_prompt)
        output = json.loads(response.text)
        if output["customer_id"] != 'NAN':
            # load the customer_id from db
            customer_datas = self.get_df(sheet_name=SHEET_NAME, worksheet_name="customer_profile")
            # search for the customer_id
            try:
                customer_data = customer_datas[customer_datas["CustomerID (Primary Key)"] == output["customer_id"]]
                output["customer_data"] = customer_data
            except:
                output["customer_data"] = "NAN"
            output["customer_data"] = customer_data
        return output

    def generate_travel_itinerary(self, message, pure_LLM=False, stream=False, version=2):
        # Firstly check if prompt or other fields exists in message
        if "prompt" in message:
            initial_prompt = message["prompt"]
            # break this prompt down into destination, dates, duration, number_of_pax, filter, budget
            print(f"Prompt: {message['prompt']}")
            message = self.prompt_intent_classifier(message["prompt"])
            message["prompt"] = initial_prompt
            print(f"----> {message}")
        else:
            # use the other fields to generate the travel package
            pass
        
        if not pure_LLM:
            # Load the inventory
            print("Loading inventory...")
            df = self.get_df(sheet_name=SHEET_NAME, worksheet_name=WORKSHEET_NAME)

            # Filter inventory based on destination
            print("Filtering inventory...")
            columns_to_embed = ["Country", "Location"]
            column_title = "Title"
            top_inventories = self.filter_destinations(message["destination"],
                                                        df, 
                                                        columns_to_embed = columns_to_embed,
                                                        column_title=column_title,
                                                        top_N = 5)

            print(top_inventories)
            top_inventories_json = top_inventories.to_json(orient='records')
            # pickle this top_inventories_json
            # x = pickle_this(top_inventories_json, pickle_name="top_inventories", path="./database/top_inventories/")
        else:
            top_inventories_json = None
        print("Generating itinerary...")
        # prompt the user to generate the travel package
        if stream:
            return self.generate_travel_package_foundational(message, top_inventories_json, pure_LLM=pure_LLM, stream=stream, version=version)
        else:
            itinerary_payload = self.generate_travel_package_foundational(message, top_inventories_json, pure_LLM=pure_LLM, version=version, stream=stream)
            return itinerary_payload

    def fix_json(self,text):
        # Regex pattern to find missing commas after activity objects
        pattern = r"(\}\s*){"  
        # Replace missing commas with comma and space
        corrected_text = re.sub(pattern, "}, ", text)
        return corrected_text
    
    def generate_travel_package_foundational(self, 
                                             message, 
                                             top_inventories = None,
                                             pure_LLM=False, 
                                             stream=False, 
                                             version=2):
        """
        This function will consume message with keys:
        * destination
        * dates
        * duration
        * number_of_pax
        * filter (tags: https://docs.google.com/spreadsheets/d/1R1jdX8PKyIhYu8F6vdj4ZpddITkZnMo_5Ri52XDf_5U/edit#gid=0)
        * budget
        """
        # check if message["prompt"] is empty or "" or None, then use the other fields to generate the travel package
        # else use only "prompt"
        # check if message["prompt"] exists: if it does, use it to extract the destination
        # check if "prompt" exists in message dict
        # timestamp id
        timestamp_id = time.time_ns()

        if version == 1:
            travel_package_inner_prompt_ = travel_package_inner_prompt_1
            travel_jsonSchema_ = travel_jsonSchema_1
        else:
            travel_package_inner_prompt_ = travel_package_inner_prompt_2
            travel_jsonSchema_ = travel_jsonSchema_2
        if pure_LLM:
            client_requirements = f"""
                            * prompt: {message["prompt"]} 
                            """
            top_inventories = None
        else:
            client_requirements = f"""
                                * destination: {message["destination"]}
                                * dates: {message["dates"]}
                                * duration: {message["duration"]} days
                                * number of pax: {message["number_of_pax"]} people
                                * tags: {message["filter"]}
                                * budget: {message["budget"]}
                                """
        # try to extract out "customer_id" from message if available, else set to "NAN"
        try:
            customer_id = message["customer_id"]
        except:
            customer_id = "NAN"
            # use LLM to extract out destination from the prompt
        if message["duration"] > 7:

            travel_package_prompt = f"""You are a travel agent creating a comprehensive itinerary. However you are given a client requirement that is not feasible. The client requires a trip that is more than 10 days.
            
            Return the JSONschema strictly:
            <JSONSchema>{json.dumps(NULL_DURATION_RESPONSE)}</JSONSchema>
            """
        elif message["number_of_pax"] > 10:
            travel_package_prompt = f"""You are a travel agent creating a comprehensive itinerary. However you are given a client requirement that is not feasible. The client requires a trip for more than 10 pax.
            
            Return the JSONschema strictly:
            <JSONSchema>{json.dumps(NULL_PAX_RESPONSE)}</JSONSchema>
            """
        elif message["destination"] == "NAN":
            travel_package_prompt = f"""You are a travel agent creating a comprehensive itinerary. However you are given a client requirement that is not feasible. The client requires a trip to a fictional or nonsensical destination.
            
            Return the JSONschema strictly:
            <JSONSchema>{json.dumps(NULL_DESTINATION_RESPONSE)}</JSONSchema>
            """
        else:
            travel_package_prompt = f"""You are a travel agent creating a comprehensive itinerary given CLIENT REQUIREMENTS and AVAILABLE INVENTORY.
        
            ****INPUTS****
            ***CLIENT REQUIREMENTS:***
            IMPORTANT: The itinerary must strictly adhere to the client requirements: destination, dates, duration, number of pax, tags, budget;
            Do not produce flight based itineraries, eg: "return to airport to relax for the day"
            IMPORTANT: make sure the number of days required is adhered to. If 7 days are required, there MUST BE 7 days in the itinerary generated.
            IMPORTANT: Make sure itinerary caters for the number of pax, eg: if for family, ensure child-friendly activities are included.
            IMPORTANT: Make sure itinerary caters to the tags and customer_data if provided.
            {client_requirements}
            ***AVAILABLE INVENTORY:***
            {top_inventories}
            Following content outline:
            {travel_package_inner_prompt_}

            Follow the JSONschema strictly (from the content ouline above) fill in all required fields:
            <JSONSchema>{json.dumps(travel_jsonSchema_)}</JSONSchema>
            """
        self.model = self.build_model(self.model_name, api_key=self.GEMINI_API_KEY)
        # measure token count
        total_input_tokens = self.count_tokens(self.model, travel_package_prompt)
        print(f"Token count INPUT: {total_input_tokens.total_tokens} -- INPUT COST: ${total_input_tokens.total_tokens * (7/1e6)}")
        if stream:
            # since cant invoke prompt, just return the travel_package_prompt
            return message, travel_package_prompt
        else:
            response_travel_package = self.prompt(self.model, travel_package_prompt, stream = stream)

            total_output_tokens = self.count_tokens(self.model, response_travel_package.text)
            print(f"Token count OUTPUT: {total_output_tokens.total_tokens} -- OUTPUT COST: ${total_output_tokens.total_tokens * (21/1e6)}")
            print(response_travel_package.text)               
            # do update_google_sheet without wating for response, and just return payload
            t1 = time.time()
            corrected_json_text = self.fix_json(response_travel_package.text)
            self.update_google_sheet(timestamp_id,customer_id, str(message), corrected_json_text)
            t2 = time.time()
            print(f"Time taken to update Google Sheet: {t2-t1}")
            return {"prompt": travel_package_prompt, "response": response_travel_package, "total_input_tokens": total_input_tokens, "total_output_tokens": total_output_tokens}
        






















