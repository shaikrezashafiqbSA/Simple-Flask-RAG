import re
import numpy as np
import pandas as pd
import json
from settings import GEMINI_API_KEY
import google.generativeai as genai
from gdrive.gdrive_handler import GspreadHandler

from scipy.spatial.distance import cosine
from utils.pickle_helper import pickle_this

CREDENTIALS_FILE = 'smart-platform.json'
SHEET_NAME = "Master Database" 
WORKSHEET_NAME = "inventory_processed"
class traveller:
    def __init__(self,
                 generation_config = None,
                 block_threshold="BLOCK_NONE"):
        # To be generalised for other LLMs in the future
        # self.co = cohere.Client(COHERE_API_KEY)
        genai.configure(api_key = GEMINI_API_KEY, )
        self.model_name = "gemini-1.5-pro-latest"
        self.embed_model = 'models/embedding-001'

        """
        API_KEY: str
            The API key for the Google Generative AI API
            BLOCK_NONE = Always show regardless of probability of unsafe content
            BLOCK_ONLY_HIGH = Block when high probability of unsafe content
            BLOCK_MEDIUM_AND_ABOVE = Block when medium or high probability of unsafe content
            BLOCK_LOW_AND_ABOVE = Block when low, medium or high probability of unsafe content
        """
        self.GEMINI_API_KEY = GEMINI_API_KEY
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
                                        "max_output_tokens": 40000,}
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

        self.model = self.build_model(self.model_name)


    def build_model(self, model_name):
        genai.configure(api_key = self.GEMINI_API_KEY)

        model = genai.GenerativeModel(model_name=model_name,
                                        generation_config=self.generation_config,
                                        safety_settings=self.safety_settings)
        
        return model
    def count_tokens(self, text):
        return self.model.count_tokens(text)
    
    def prompt(self, query):
        response = self.model.generate_content(query)
        # print(response.text)
        return response

    def get_df(self, sheet_name, worksheet_name):
        gspread_handler = GspreadHandler(credentials_filepath=CREDENTIALS_FILE)
        df = gspread_handler.get_sheet_as_df(sheet_name=sheet_name, worksheet_name=worksheet_name)
        return df


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
    


    # def retrieve1(self, query_embedding, embeddings, chunks, top_N = 5, verbose = False):
    #     # Calculate similarity between the user question & each chunk
    #     similarities = [self.cosine_similarity(query_embedding, chunk) for chunk in embeddings]
    #     if verbose:
    #         print("similarity scores: ", similarities)

    #     # Get indices of the top 10 most similar chunks
    #     sorted_indices = np.argsort(similarities)[::-1]

    #     # Keep only the top 10 indices
    #     top_indices = sorted_indices[:top_N]

    #     # Retrieve the top 10 most similar chunks
    #     top_chunks_after_retrieval = [chunks[i] for i in top_indices]
    #     if verbose:
    #         print(f"Here are the top {top_N} inventories after retrieval: ")
    #         for t in top_chunks_after_retrieval:
    #             print("== " + t)

    #     return top_chunks_after_retrieval
    

    def filter_destinations(self, destination_query, df, columns_to_embed=["Country", "Location"], column_title="Title", top_N=5):
        # # combine the columns to embed
        df['destination'] = df[columns_to_embed].apply(lambda row: ' '.join([str(x) for x in row]), axis=1)
        # Create a regex pattern to find the query anywhere in the destination string (case-insensitive)
        pattern = re.compile(re.escape(destination_query), re.IGNORECASE)

        # Filter the DataFrame based on regex matches in the specified column
        filtered_df = df[df['destination'].astype(str).str.contains(pattern)]
        # drop destination column
        filtered_df = filtered_df.drop(columns=['destination'])
        filtered_df = filtered_df[["Type", "Tags", "Title", "Description", "VendorID"]]
        filtered_inventories_json = filtered_df.to_json(orient='records')
        return filtered_inventories_json

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
    
    def generate_travel_itinerary(self, message):
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
        print("Generating itinerary...")
        # prompt the user to generate the travel package
        itinerary_payload = self.generate_travel_package_foundational(message, top_inventories)
        return itinerary_payload


    def generate_travel_package_foundational(self, 
                                             message, 
                                             top_inventories = None,):
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
        if message["prompt"] == "" or message["prompt"] is None:
            client_requirements = f"""
                                * destination: {message["destination"]}
                                * dates: {message["dates"]}
                                * duration: {message["duration"]}
                                * number of pax: {message["number_of_pax"]}
                                * tags: {message["filter"]}
                                * budget: {message["budget"]}
                                """
        else:
            client_requirements = f"""
                                    * user prompt: {message["prompt"]}
                                    """
            # use LLM to extract out destination from the prompt

        jsonSchema = {
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

        travel_package_prompt = f"""You are a soulful and poetic travel agent creating a comprehensive itinerary given client requirements and available inventory.

        ****INPUTS****
        ***Client Requirements:***
        {client_requirements}

        ***Available inventory:***
        {top_inventories} 

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

        Follow the JSON schema strictly and fill in all required fields.

        <JSONSchema>{json.dumps(jsonSchema)}</JSONSchema>
        """

        

        response_travel_package = self.prompt(travel_package_prompt)    
        print(response_travel_package.text)   
        self.response_travel_package = response_travel_package.text              
        return {"prompt": travel_package_prompt, "response": response_travel_package}