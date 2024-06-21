import re
import numpy as np
import pandas as pd
import json
import time 
from settings import GEMINI_API_KEY1 as GEMINI_API_KEY1
from settings import GEMINI_API_KEY as GEMINI_API_KEY
import google.generativeai as genai
from gdrive.gdrive_handler import GspreadHandler

from scipy.spatial.distance import cosine
from utils.pickle_helper import pickle_this
from prompt_engineering.jsonSchemas import intent_jsonSchema, travel_jsonSchema_1, travel_jsonSchema_2
from prompt_engineering.responses import EMPTY_RESPONSE, NULL_RESPONSE
from prompt_engineering.travel_agent import travel_package_inner_prompt_1, travel_package_inner_prompt_2

CREDENTIALS_FILE = 'smart-platform.json'
SHEET_NAME = "Master Database" 
WORKSHEET_NAME = "inventory_processed"


class EmptyResponse:
    def __init__(self, text):
        self.text = text


class traveller:
    def __init__(self,
                 generation_config = None,
                 block_threshold="BLOCK_NONE", ):
        self.GEMINI_API_KEY1 = GEMINI_API_KEY
        self.GEMINI_API_KEY = GEMINI_API_KEY1
        self.model_name = "gemini-1.5-flash" 
        # self.model_name = "gemini-1.5-pro-latest"
        self.embed_model = 'models/embedding-001'
        if generation_config is None:
            # self.generation_config =glm.GenerationConfig(response_mime_type="application/json",
            #                                              response_schema="application/json",
            #                                             temperature=0.9,  
            #                                             top_p=0.95,
            #                                             top_k=40,
            #                                             max_output_tokens=40000,  
            #                                         )
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

    def update_google_sheet(self, timestamp, prompt, itinerary):
        gspread_handler = GspreadHandler(credentials_filepath=CREDENTIALS_FILE)
        """Updates the Google Sheet with the extracted text."""
        data = [{"timestamp":'"'+str(timestamp)+'"', "prompt": prompt, "itinerary": itinerary}]
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
        filtered_df = filtered_df[["Type", "Tags", "Title", "Description", "Vendor ID", "Activity ID"]]
        # drop duplicates by title
        filtered_df = filtered_df.drop_duplicates(subset=[column_title])

        
        return filtered_df
    
    def prompt_intent_classifier(self, message):
        """
        Example prompt: "i want to go to perlis for a hidden gems trip"
        will extract out destination, dates, duration, number_of_pax, tags, budget if available

        """
        user_intent_prompt = f"""You are a travel assistant. A user wants to go on a trip. 
        Extract the following details if available: destination, dates, duration, number_of_pax, tags, and budget. 
        If a detail is not mentioned, leave it as 'NAN'.
        If duration is NAN, assume it is a 3-day trip for 1 person.
        IMPORTANT: If the destination is fictional or nonsensical, return 'NAN' for destination.
        <User Input>:
        {message}
        Follow the JSON schema strictly and fill in all required fields.
        <JSONSchema>{json.dumps(intent_jsonSchema)}</JSONSchema>
        """

        model = self.build_model(self.model_name, api_key=self.GEMINI_API_KEY) 
        response = self.prompt(model, user_intent_prompt)
        output = json.loads(response.text)
        return output

    def generate_travel_itinerary(self, message, duo=False, pure_LLM=False, stream=False, version=2):
        # Firstly check if prompt or other fields exists in message
        if "prompt" in message:
            initial_prompt = message["prompt"]
            # break this prompt down into destination, dates, duration, number_of_pax, filter, budget
            print(f"Prompt: {message['prompt']}")
            message = self.prompt_intent_classifier(message["prompt"])
            message["prompt"] = initial_prompt
            # check if message["destination"] is "NAN"
            if message["destination"] == "NAN":

                empty_response = EmptyResponse(json.dumps(EMPTY_RESPONSE))
                # return empty response in format: itinerary_payload["response"].text)
                itinerary_payload = {"prompt": message, "response": empty_response}
                return itinerary_payload
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
        else:
            top_inventories_json = None
        print("Generating itinerary...")
        # prompt the user to generate the travel package
        if stream:
            return self.generate_travel_package_foundational(message, top_inventories_json, duo=duo, pure_LLM=pure_LLM, stream=stream, version=version)
        else:
            itinerary_payload = self.generate_travel_package_foundational(message, top_inventories_json, duo=duo, pure_LLM=pure_LLM, version=version, stream=stream)
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
                                             duo=False,
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
                                * duration: {message["duration"]}
                                * number of pax: {message["number_of_pax"]}
                                * tags: {message["filter"]}
                                * budget: {message["budget"]}
                                """
            # use LLM to extract out destination from the prompt

        travel_package_prompt = f"""You are a travel agent creating a comprehensive itinerary given client requirements and available inventory.

        ****INPUTS****
        ***Client Requirements:***
        IMPORTANT: The itinerary must strictly adhere to the client requirements: duration, destination, tags, budget;
        {client_requirements}
        ***Available inventory:***
        {top_inventories}
        Following content outline:
        {travel_package_inner_prompt_}
        Follow the JSON schema strictly (from the content ouline above) fill in all required fields:
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
            self.update_google_sheet(timestamp_id, str(message), corrected_json_text)
            t2 = time.time()
            print(f"Time taken to update Google Sheet: {t2-t1}")
            return {"prompt": travel_package_prompt, "response": response_travel_package, "total_input_tokens": total_input_tokens, "total_output_tokens": total_output_tokens}
        

























# ========================================================================================================
# embedding methods for bigger databases
# ========================================================================================================


    def embed_text(self,
                   text,
                   title=None,
                   task_type="retrieval_document", 
                   model='models/embedding-001', ):
        """
        Task Type	                    Description
        retrieval_query
            	Specifies the given text is a query in a search/retrieval setting.
        retrieval_document
            	Specifies the given text is a document in a search/retrieval setting.
        semantic_similiarity
            	Specifies the given text will be used for Semantic Textual Similarity (STS).
        classification
            	Specifies that the embeddings will be used for classification.
        clustering
            	Specifies that the embeddings will be used for clustering.

        """
        return genai.embed_content(model=model,
                                    content=text,
                                    task_type=task_type,
                                    title=title)["embedding"]
    
    def embed_df(self,
                 df,
                 title="Title",
                 text="Text"):

        df['Embeddings'] = df.apply(lambda row: self.embed_text(str(row[title]), str(row[text]), model=self.embed_model), axis=1)

        return df

    def embed_query(self, query):

        return genai.embed_content(model=self.embed_model,
                                   content=query,
                                   task_type="retrieval_query")["embedding"]

    def retrieve(self,
                query_embedding, 
                dataframe, 
                top_N = 1,
                similiarity_calculation = "raw_dot") -> pd.Series:
        """
        Compute the distances between the query and each document in the dataframe
        using the dot product.

        Returns:
            A pd.Series containing a DataFrame with two columns:
                - 'Text': The text of the top N passages.
                - 'Score': The corresponding similarity score for each passage.
        """

        # format the dataframe to select which columns to embed

        if similiarity_calculation == "raw_dot":
            dot_products = np.dot(np.stack(dataframe['Embeddings']), query_embedding["embedding"])
            idx = np.argsort(dot_products)[-top_N:][::-1]

            # Create a DataFrame with passages and scores
            top_passages = pd.DataFrame({'Text': dataframe.iloc[idx]['Text'], 'Score': dot_products[idx]})

            # Return the DataFrame as a Series with a descriptive name
            return top_passages.reset_index(drop=True).rename(columns={'Text': 'Passage', 'Score': 'Similarity Score'})
        else:
            # NOT TESTED
            # Cosine Similarity Calculation
            dataframe['Similarity Score'] = dataframe['Embeddings'].apply(
                lambda x: 1 - cosine(x, query_embedding) 
            )

            # Efficient Top N Selection
            top_passages = dataframe.nlargest(top_N, 'Similarity Score')[['Text', 'Similarity Score']]
            top_passages.reset_index(drop=True, inplace=True)

            return top_passages.rename(columns={'Text': 'Passage'})
    

    def rag_pipeline(self, query, sheet_name, worksheet_name, reembed= False):
        # 1) Load data
        df = self.get_df(sheet_name, worksheet_name)

        # 2) Embed data
        if reembed:
            embeddings = self.embed_df(df)
            pickle_this(embeddings, pickle_name=f"{sheet_name}_{worksheet_name}", path = "./database/embeddings/")
        else:
            embeddings = pickle_this(pickle_name=f"{sheet_name}_{worksheet_name}", path = "./database/embeddings/")

        # 3) Embed query
        query_embedding = self.embed_query(query=query)

        # 4) Retrieve top chunks
        top_chunks_after_retrieval = self.retrieve(query_embedding, embeddings, list(df["meta_data"]))

        # 5) Generate augmented response
        response = self.augmented_generation(query, top_chunks_after_retrieval)
        return response