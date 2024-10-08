"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""
    

import numpy as np
import pandas as pd


from pathlib import Path
import google.generativeai as genai


class GHandler:
    """
    This class is a wrapper around the Google Generative AI API 
    (to be generalised for other generative AI APIs in the future)

    It allows the user to easily interact with the API and perform various tasks
    It has the following features 
    1) text --> text                  ---- IMPLEMENTED
    2) text + image --> text          ---- IMPLEMENTED
    3) text + image --> text + image  ---- !! global tech not there yet; Gemini lacks !!
    4) text + video --> text          ---- https://github.com/mytechnotalent/Gemini
    5) text + video --> text + video  ---- !! global tech not there yet; SORA) !!

    """ 

    def __init__(self, API_KEY, 
                 generation_config = {"temperature": 0.9,
                                      "top_p": 0.95,
                                      "top_k": 40,
                                      "max_output_tokens": 40000,
                                      },
                 block_threshold="BLOCK_NONE"):
        """
        API_KEY: str
            The API key for the Google Generative AI API
            BLOCK_NONE = Always show regardless of probability of unsafe content
            BLOCK_ONLY_HIGH = Block when high probability of unsafe content
            BLOCK_MEDIUM_AND_ABOVE = Block when medium or high probability of unsafe content
            BLOCK_LOW_AND_ABOVE = Block when low, medium or high probability of unsafe content
        """
        self.API_KEY = API_KEY
        self.generation_config = generation_config
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

        
    def build_model(self, model_name,):
        genai.configure(api_key = self.API_KEY)

        model = genai.GenerativeModel(model_name=model_name,
                                        generation_config=self.generation_config,
                                        safety_settings=self.safety_settings)
        
        return model
    

    def show_available_models(self,):
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)


    def prompt(self, prompt,model_name="gemini-pro"):
        model = self.build_model(model_name)
        response = model.generate_content(prompt)
        # print(response.text)
        return response
    

    def prompt_image(self,
                     image_path,
                     prompt_1,
                     prompt_2 = None,
                     model_name="gemini-pro-vision",
                     ):
        # Set up the model
        model = self.build_model(model_name)

        # Validate that an image is present
        if not (img := Path(image_path)).exists():
            raise FileNotFoundError(f"Could not find image: {img}")

        image_parts = [
            {
            "mime_type": "image/jpeg",
            "data": Path(image_path).read_bytes()
            },
        ]

        if prompt_2 is None:
            prompt_parts = [
                prompt_1,
                image_parts[0],
            ]
        else:
            prompt_parts = [
                prompt_1,
                image_parts[0],
                prompt_2,
            ]

        response = model.generate_content(prompt_parts)
        return response

    
    def embed_text(self,
                  title,
                  text,
                  model='models/embedding-001', ):
        """
        Usage: 
            df['Embeddings'] = df.apply(lambda row: embed_fn(row['Title'], row['Text']), axis=1)
            df
        """
        return genai.embed_content(model=model,
                                    content=text,
                                    task_type="retrieval_document",
                                    title=title)["embedding"]
    
    def embed_df(self,
                 df,
                 title="Title",
                 text="Text",
                 model='models/embedding-001', ):
        assert title in df.columns, f"title: '{title}' column not found in dataframe"
        assert text in df.columns, f"text: '{text}' column not found in dataframe"
        

        df['Embeddings'] = df.apply(lambda row: self.embed_text(str(row[title]), str(row[text]), model=model), axis=1)

        return df

    # Document SEARCH WITH Q&A

    def retrieval_query(self, query):
        model = 'models/embedding-001'

        return genai.embed_content(model=model,
                                    content=query,
                                    task_type="retrieval_query")["embedding"]
        
    def find_best_passage(self,
                          content, 
                          dataframe, 
                          topN = 1,
                          task_type="retrieval_query",
                          model='models/embedding-001') -> pd.Series:
        """
        Compute the distances between the query and each document in the dataframe
        using the dot product.

        Returns:
            A pd.Series containing a DataFrame with two columns:
                - 'Text': The text of the top N passages.
                - 'Score': The corresponding similarity score for each passage.
        """

        query_embedding = genai.embed_content(model=model,
                                                content=content,
                                                task_type=task_type)
        dot_products = np.dot(np.stack(dataframe['Embeddings']), query_embedding["embedding"])
        idx = np.argsort(dot_products)[-topN:][::-1]

        # Create a DataFrame with passages and scores
        top_passages = pd.DataFrame({'Text': dataframe.iloc[idx]['Text'], 'Score': dot_products[idx]})

        # Return the DataFrame as a Series with a descriptive name
        return top_passages.reset_index(drop=True).rename(columns={'Text': 'Passage', 'Score': 'Similarity Score'})

    

    
    def count_tokens(self, text, model):
        model = genai.GenerativeModel('models/gemini-1.0-pro-latest')
        model.count_tokens(text)