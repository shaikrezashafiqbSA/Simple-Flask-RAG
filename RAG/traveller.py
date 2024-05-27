import re
import numpy as np
import pandas as pd
import json
from settings import GEMINI_API_KEY
import google.generativeai as genai
import google.ai.generativelanguage as glm
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
            self.generation_config =glm.GenerationConfig(response_mime_type="application/json",
                                                        temperature=0.9,  
                                                        top_p=0.95,
                                                        top_k=40,
                                                        max_output_tokens=40000,  
                                                    )
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
        filtered_df = filtered_df[["Type", "Tags", "Title", "Description"]]
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
                                "type": "object",
                                "properties": {
                                    "day1_summary": {"type": "string"},
                                    "day1_itinerary": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "title": {"type": "string"},
                                                "text": {"type": "string"},
                                                "inventory": {"type": "string"},  # 'available!' or 'unavailable!'
                                                "price": {"type": "number"}
                                            }
                                        }
                                    },
                                    "day2_summary": {"type": "string"},
                                    "day2_itinerary": {
                                        "type": "array", 
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "title": {"type": "string"},
                                                "text": {"type": "string"},
                                                "inventory": {"type": "string"},
                                                "price": {"type": "number"}
                                            }
                                        }
                                    }
                                }
                            },
                            "pricing": {
                                "type": "object",
                                "properties": {
                                    "total_cost": {"type": "number"},  
                                    "per_day_cost": {"type": "number"},
                                    "per_activity_cost": {"type": "string"}  
                                }
                            }
                        },
                        "required": ["summary", "itinerary", "pricing"]  # Ensure all sections are present
                        }    
        travel_package_prompt = f"""You are a travel agent creating a comprehensive itinerary given client requirements and available inventory.
                                    ****INPUTS****
                                    ***Client Requirements:***
                                    {client_requirements}

                                    ***Available inventory:***
                                    {top_inventories}   

                                    ****OUTPUT****
                                    IMPORANT NOTE: The itinerary must only include the following sections:

                                    ***summary***
                                    Write an engaging one-paragraph summary containing 100 words to recommend the destination.
                                    Open with a captivating sentence and how it aligns with the traveller's interests (based on tags and the itinerary generated below)
                                    Expand on each tags, briefly describe what the destination offers related to each tag, using persuasive language.
            
                                    ***itinerary***
                                    Must contain, for EACH day, a 100 word summary of the day planned. it must have activities planned around breakfast > lunch > dinner (based on inventory else suggest). 
                                    Then for each day, walk through the activities (MUST contain 100 word vivid, persuasive description for EACH activity)
                                    ALSO include pricing and availability for each activity (if available from the inventory else state unavailable)
                                    NOTE: MUST FOLLOW THE FOLLOWING FORMAT
                                    '''
                                    "day 1 summary": "Welcome to Aceh, Indonesia! You're in for an amazing first day of your trip. To start off, head to Lampuuk Beach, a hidden gem known for its pristine white sand and crystal-clear water. Spend some time relaxing and enjoying the beautiful scenery. Next, visit the iconic Baiturrahman Grand Mosque, a historical landmark that showcases stunning architecture. Take a moment to admire the intricate details and learn about its significance. For lunch, try Canai Mamak, a local eatery known for its delicious traditional cuisine. Afterward, make your way to the Aceh Tsunami Museum, a thought-provoking attraction that pays tribute to the resilience of the Acehnese people. End the day with a visit to Warung Makan Hasan 3, Cabang Kreung Cut, another fantastic eatery where you can indulge in authentic Acehnese dishes. Enjoy your first day in Aceh!"
                                    "day 1 itinerary": 
                                    *1*: "title": "Lampuuk Beach", "text": "Lampuuk Beach in Banda Aceh is a captivating destination that aligns perfectly with your interests in Hidden Gems, Historical Landmarks, and Arts & Theatre. This serene beach offers a unique blend of natural beauty and historical significance. As you explore the area, you will discover hidden gems tucked away along the coastline, providing a sense of adventure and discovery. Lampuuk Beach also holds historical importance, with remnants of Aceh's rich heritage scattered throughout the area. The beach provides a picturesque setting for capturing stunning photographs and immersing yourself in the local culture. Whether you're strolling along the shoreline, admiring the historical landmarks, or enjoying the arts and theatre performances held nearby, Lampuuk Beach promises an unforgettable experience for your solo trip to Aceh.","inventory": "unavailable", "Price": "estimated $40"
                                    *2* ...
                                    *3* ...
                                    
                                    "day n summary": "On the nth day of your trip to Aceh, Indonesia, you will have the opportunity to explore some hidden gems and historical landmarks. Start your day by visiting Alue Naga Beach, a beautiful and secluded spot where you can relax and enjoy the serene surroundings. Afterward, head to Warung Nasi Kambing Lem Bakrie, a local eatery known for its delicious Indonesian cuisine. Next, visit Rahmatullah Mosque, a historical landmark known for its stunning architecture and cultural significance. In the afternoon, make your way to Kuta Malaka Water Boom, a popular attraction where you can have fun and cool off in the water. Finally, end your day at Banda Seafood, a renowned eatery where you can indulge in fresh and flavorful seafood dishes. Enjoy your day exploring these wonderful locations in Aceh!"
                                    "day n itinerary":
                                    *1*: "title":"Alue Naga Beach","text": "Located in Banda Aceh, Indonesia is a captivating destination that perfectly aligns with your interests in Hidden Gems, Historical Landmarks, and Arts & Theatre. This picturesque beach offers a serene and secluded atmosphere, making it a true hidden gem. As you explore the area, you'll discover traces of history, including remnants of the devastating 2004 tsunami, which adds a profound historical significance to the beach. Moreover, Alue Naga Beach serves as a vibrant hub for local arts and theater, providing you with the opportunity to witness and appreciate the rich cultural heritage of Aceh. With its breathtaking beauty, historical significance, and artistic charm, Alue Naga Beach is sure to offer you a memorable and fulfilling experience during your solo trip to Aceh.", "inventory": "vendor ID: x", Price: $50"
                                    *2* ...
                                    *3* ...
                                    '''
                                    ***pricing***
                                    * Calculate the total package cost. Reference the Available Inventory for pricing if available, else state "unavailable" for all fields. 
                                    
                                    Follow the JSON schema strictly and fill in all required fields.
                                    <JSONSchema>{json.dumps(jsonSchema)}</JSONSchema>

                    """

        

        response_travel_package = self.prompt(travel_package_prompt)    
        print(response_travel_package.text)   
        self.response_travel_package = response_travel_package.text              
        return {"prompt": travel_package_prompt, "response": response_travel_package}