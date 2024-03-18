# smart-travels
## README: smart-travels - Retrieval Augmented Generation for Travelers

This repository provides a Proof of Concept (POC) implementation of a Retrieval Augmented Generation (RAG) model for Smart World Travel. The RAG model is designed to assist travelers by generating creative text formats, like travel itineraries or trip descriptions, based on user prompts and retrieved information from a Curated DATABASE.

**Getting Started:**

This POC requires Python and its package manager `pip` to be installed on your system.

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

# refer to jupyter notebook for the code

```python

from RAG.librarian import Librarian 

librarian = Librarian(librarian_LLM_model = "GEMINI")

# SELECT SPECIALIST DATABASE
librarian.select_specialist(specialist = "traveller", specialist_LLM_model = "GEMINI", )

# Ask librarian to get acquinted with the specialist database
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


**Further Considerations:**

* This is a POC, and the RAG model performance might improve with fine-tuning on travel-specific data.
* Consider including a `LICENSE` file if you have any specific licensing requirements for your code.

**Disclaimer:**

This POC is provided for demonstration purposes only. It is recommended to consult with travel professionals for planning your trips.
