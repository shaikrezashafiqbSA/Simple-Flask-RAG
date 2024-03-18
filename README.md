# smart-travels
## README: smart-travels - Retrieval Augmented Generation for Travelers

This repository provides a Proof of Concept (POC) implementation of a Retrieval Augmented Generation (RAG) model for Smart World Travel. The RAG model is designed to assist travelers by generating creative text formats, like travel itineraries or trip descriptions, based on user prompts and retrieved information from a Curated DATABASE.

**Getting Started:**

This POC requires Python 3.12.2 (https://www.get-python.org/downloads/release/python-3122/) 
and its package manager `pip` to be installed on your system.


1. **Clone the Repository:**

   ```bash
   git clone https://github.com/calllevels/smart-travels
   ```

2. **Install Dependencies:**

   The required dependencies are listed in the `requirements.txt` file. Install them using:

   ```bash
   pip install -r requirements.txt
   ```

**Using the RAG Model (**This section might need adjustments based on your specific implementation**):**

# Refer to Traveller_POC.ipynb for the code

3. **Initialize the Librarian:**

   The `Librarian` class is the main interface to the RAG model. It provides methods to select a specialist database and to interact with the RAG model.

   ```python
   from RAG.librarian import Librarian

   librarian = Librarian(librarian_LLM_model = "GEMINI")
   ```

4. **Select a Specialist Database:**
   
      The RAG model is designed to work with specialist databases. You can select a specialist database using the `select_specialist` method.
   
      ```python
      librarian.select_specialist(specialist = "traveller", specialist_LLM_model = "GEMINI")
      ```

5. **Load Data Model:**

   The `load_data_model` method is used to load the data model for the selected specialist database. The `reembed` parameter is used to specify whether to re-embed the data model. The `embed_id` parameter is used to specify the embedding ID. The `data_model_keys` parameter is used to specify the keys for the data model tables. The `reembed_table` parameter is used to specify whether to re-embed the data model tables.

   ```python
   librarian.Traveller.load_data_model(reembed = False,
                                       embed_id = 0,
                                       data_model_keys = {"TEST - CLIENT":"CLIENT ID",
                                                           "TEST - CLIENT REQUEST":"CLIENT ID",
                                                           "TEST - FLIGHTS":"FLIGHT ID",
                                                           "TEST - ACCOMODATIONS":"ACCOMODATION ID",
                                                           "TEST - ACTIVITIES":"ACTIVITY ID",
                                                           "TEST - SERVICES":"SERVICE ID",
                                                           },
                                       reembed_table = {"TEST - CLIENT":True,
                                                       "TEST - CLIENT REQUEST":True,
                                                       "TEST - FLIGHTS":True,
                                                       "TEST - ACCOMODATIONS":True,
                                                       "TEST - ACTIVITIES":True,
                                                       "TEST - SERVICES":True,
                                                       }
                                       )
   ```

6. **Generate Text:**
   
```python
# Ask Traveller to generate a travel package
initial_query = "Hafeez from Kuala Lumpur wants to go Bali for 4 days for 2 pax. Budget: $2000. I want to chill at the beach"
convo_package = librarian.Traveller.III_generate_travel_package(initial_query = initial_query,
                                                                 topN = 6, 
                                                                 model_name = "gemini-pro",
                                                                 )
```

**Further Considerations:**

* This is a POC, and the RAG model performance might improve with fine-tuning on travel-specific data.


