import io
import re
import time
from __future__ import print_function
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

from gdrive.gdrive_handler import GspreadHandler

from pdf2image import convert_from_path
import os
import pandas as pd
from settings import GEMINI_API_KEY
from llm_handler.GHandler import GHandler
import fitz  # Import PyMuPDF

# Replace with your credentials file path
CREDENTIALS_FILE = 'smart-platform.json'
SHEET_NAME = "Master Database" 
WORKSHEET_NAME = "inventory"

gspread_handler = GspreadHandler(credentials_filepath=CREDENTIALS_FILE)

def gemini_ocr(file_path):
    """Performs OCR on the given PDF using Gemini and returns extracted text."""
    ghandler = GHandler(GEMINI_API_KEY, generation_config={"temperature": 0.9, "top_p": 0.95, "top_k": 40, "max_output_tokens": 40000}, block_threshold="BLOCK_NONE")
    prompt = "You are an OCR bot. Extract ALL the text from the image as raw text. Ensure all pricing, phone numbers, and emails are extracted ACCURATELY. OCR text output is sometimes wrong, so correct it where needed."

    doc = fitz.open(file_path)
    extracted_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))  # Increase resolution for better OCR
        image_path = file_path.replace('.pdf', f'_page_{page_num + 1}.jpg')
        pix.save(image_path)  # Save each page as an image
        try:
            response = ghandler.prompt_image(image_path=image_path, prompt_1=prompt, prompt_2=None, model_name="gemini-pro-vision")
            print(response)
            extracted_text += response.text
        except Exception as e:
            print(f"An error occurred for {file_path} - skipping: {e}")
        os.remove(image_path)  # Clean up the image file

    return extracted_text


def extract_folder_id(url):
    """Extracts the folder ID from a Google Drive URL using regular expressions."""

    pattern = r"folders/([A-Za-z0-9_-]+)\?"  # Pattern to match folder ID
    match = re.search(pattern, url)

    if match:
        return match.group(1)  # Return the captured folder ID
    else:
        return None  # No match found

def update_google_sheet(destination, title, text):
    """Updates the Google Sheet with the extracted text."""
    data = [{"Destination": destination, "Title": title, "Text": text}]
    df = pd.DataFrame(data)
    print(df)
    # replace with the correct sheet name 
    gspread_handler.update_cols(df, SHEET_NAME, WORKSHEET_NAME) #replace with the correct sheet name 


def get_google_drive_service():
  """Initializes the Google Drive API service."""
  scopes = ['https://www.googleapis.com/auth/drive.readonly']
  credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scopes)
  service = build('drive', 'v3', credentials=credentials)
  return service

def download_file(service, file_id, file_name):
    """Downloads the specified file from Google Drive."""
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%")

def get_folder_contents(service, folder_id):
    """Retrieves a list of PDF files within the specified folder and subfolders."""
    all_files = []
    page_token = None
    while True:
        try:
            results = service.files().list(
                pageSize=1000,  # Fetch a larger batch for efficiency
                fields="nextPageToken, files(id, name, mimeType)",
                q=f"'{folder_id}' in parents and mimeType='application/pdf'",  # Filter for PDFs
                pageToken=page_token
            ).execute()

            all_files.extend(results.get('files', []))
            page_token = results.get('nextPageToken')
            if not page_token:
                break  # No more pages

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    return all_files


def get_download_link(item):
  """Retrieves the download link for a file based on its mimeType."""
  if item['mimeType'].startswith('application/'):  # Check if it's a Google Doc
    return None  # Google Docs don't have direct download links
  else:
    return f"https://drive.google.com/uc?export=download&id={item['id']}"


def run_ETL(folder_link):
    """Main function to download, OCR, and update Google Sheets."""
    folder_id = extract_folder_id(folder_link)
    service = get_google_drive_service()
    folder_contents = get_folder_contents(service, folder_id)

    if folder_contents:
        print(f"Found {len(folder_contents)} PDF files in the specified folder.")
        for item in folder_contents:
            print(f"Processing: {item['name']}")
            file_name = item['name']
            file_id = item['id']
            # file_path = os.path.join("downloaded_pdfs", file_name)
            file_path = file_name

            print(f"Downloading: {file_name}")
            download_file(service, file_id, file_path)
            print(f"Downloaded: {file_name}")

            # Extract destination and title from file name
            parts = file_name.split('/')
            destination = parts[-2] if len(parts) > 1 else ""
            title = os.path.splitext(parts[-1])[0]

            # Perform OCR
            print(f"Performing OCR on: {file_name}")
            text = gemini_ocr(file_path)
            time.sleep(30)
            # Update Google Sheet
            print(f"Updating Google Sheet with: {file_name}")
            update_google_sheet(destination, title, text)
            
            os.remove(file_path) # remove file after using
    else:
        print("No PDF files found in the specified folder.")



