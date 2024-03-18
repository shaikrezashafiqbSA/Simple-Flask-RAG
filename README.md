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
   
**Creating a Virtual Environment (Optional but Recommended):**

### macOS/Linux:

1. Open your terminal and navigate to your project directory (e.g., `cd ~/smart-travels`).
2. Run the following command to create a virtual environment named `venv`:

   ```bash
   python3.12.2 -m venv venv
   ```

3. Activate the virtual environment:

   ```bash
   source venv/bin/activate
   ```

### Windows:

1. Open your terminal or command prompt and navigate to your project directory (e.g., `cd C:\Users\<username>\Documents\smart-travels`).
   While you cannot directly specify the Python version within the venv command on Windows, you can achieve the same result using a different approach:

   Locate the Executable for Your Desired Python Version:

   Open the Start menu and search for "Edit environment variables for your account".
   Click on "Edit the system environment variables".
   Under "System variables", find the variable named "Path" and double-click to edit it.
   Look for the directory path containing the Python executable for your desired version (e.g., C:\Python38\Scripts). Make sure this path is listed before any other Python version paths in the "Path" variable.

   OR- You can use Visual Studio Code to select the Python version you want to use (top right). Then Visual Studio Code will automatically set the path for you and prompt you to create the virtual environment with the selected Python version. Tick the requirements.txt file to install the dependencies in this virtual environment.

2. Run the following command to create a virtual environment named `venv`:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   ```bash
   venv\Scripts\activate.bat
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


7. **.env**
   
      Create a .env file in the root directory of the project and add the following environment variables:
   
      ```env
      PORT_NUMBER=5000
      OPENAI_API_KEY=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
      GEMINI_API_KEY=AIzaSyC17ij0oZODoB5is7byprgPaisnaOSIc5Y
      GOOGLE_API_KEY=AIzaSyCkUDWXXJmhvX1-Mr9fEmLWgqDn61aX58I
      PINECONE_API_KEY=7a0cd1a2-8e16-4d7a-ac7e-2138fd26944a
      PINECONE_ENVIRONMENT=northamerica-central1-gcp
      PINECONE_INDEX=adam
      PINECONE_DIMENSION=768 
      ```






