from dotenv import load_dotenv
load_dotenv()
import os 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
SHEET_NAME = os.getenv("SHEET_NAME")
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME")
WORKSHEET_PROMPTS_NAME = os.getenv("WORKSHEET_PROMPTS_NAME")

BEARER_TOKEN_SECRET_KEY = os.getenv("BEARER_TOKEN_SECRET_KEY")
