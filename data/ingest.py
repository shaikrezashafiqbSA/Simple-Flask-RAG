import json
import io
import re
import time
import os
import pandas as pd
import fitz

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

from gdrive.gdrive_handler import GspreadHandler
from llm_handler.GHandler import GHandler
from prompt_engineering.ingestion import ingestion_prompt

class GoogleDriveExtractor:
    def __init__(self, credentials_file, sheet_name, worksheet_name, gemini_api_key):
        self.credentials_file = credentials_file
        self.sheet_name = sheet_name
        self.worksheet_name = worksheet_name
        self.gemini_api_key = gemini_api_key
        self.gspread_handler = GspreadHandler(credentials_filepath=credentials_file)
        self.ghandler = GHandler(gemini_api_key, generation_config={"temperature": 0.9, "top_p": 0.95, "top_k": 40, "max_output_tokens": 40000}, block_threshold="BLOCK_NONE")

    def extract_folder_id(self, url):
        pattern = r"folders/([A-Za-z0-9_-]+)\?"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def gemini_ocr(self, file_path):
        # prompt = """You are an OCR bot. 
        # Extract ALL the text from the image as raw text. 
        # Ensure all pricing, phone numbers, and emails are extracted ACCURATELY. 
        # OCR text output is sometimes wrong, so correct it where needed.
        # """
        prompt = ingestion_prompt

        doc = fitz.open(file_path)
        extracted_text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            image_path = file_path.replace('.pdf', f'_page_{page_num + 1}.jpg')
            print(f"file_path: {file_path} --> image_path: {image_path}")
            pix.save(image_path)
            n = 0
            # keep on trying prompt_image for 3 times, sleeping 30s each time, then at 3rd time skip
            while n < 3:
                try:
                    response = self.ghandler.prompt_image(image_path, prompt, None, "gemini-pro-vision")
                    extracted_text += response.text
                    break
                except Exception as e:
                    print(f"An error occurred for {file_path} - retrying: {e}")
                    n += 1
                    time.sleep(30)
            else:
                print(f"Failed to extract text from {file_path}")
            os.remove(image_path)

        doc.close()   # Explicitly close the PyMuPDF document
        return extracted_text
    
    def update_google_sheet(self, destination, title, text):
        data = [{"Destination": destination, "Title": title, "Text": text}]
        df = pd.DataFrame(data)
        self.gspread_handler.update_cols(df, self.sheet_name, self.worksheet_name)

    def get_google_drive_service(self):
        scopes = ['https://www.googleapis.com/auth/drive.readonly']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scopes)
        return build('drive', 'v3', credentials=credentials)
    
    # def download_file(self, service, file_id, file_name):
    #     os.makedirs(os.path.dirname(file_name), exist_ok=True)
    #     request = service.files().get_media(fileId=file_id)
    #     fh = io.FileIO(file_name, 'wb')
    #     downloader = MediaIoBaseDownload(fh, request)
    #     done = False
    #     while done is False:
    #         status, done = downloader.next_chunk()
    #         print(f"Download {int(status.progress() * 100)}%")
    def download_file(self, service, file_id, file_name):
        """Downloads the specified file from Google Drive, handling root-level files."""
        # Create directory only if it's not empty
        file_dir = os.path.dirname(file_name)
        if file_dir:  # Check if directory path is not empty
            os.makedirs(file_dir, exist_ok=True)

        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_name, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%") 

    def get_folder_contents(self, service, folder_id):
        all_files = []
        page_token = None
        while True:
            try:
                results = service.files().list(
                    pageSize=1000,
                    fields="nextPageToken, files(id, name, mimeType)",
                    q=f"'{folder_id}' in parents and mimeType='application/pdf'",
                    pageToken=page_token
                ).execute()
                all_files.extend(results.get('files', []))
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
            except HttpError as error:
                print(f"An error occurred: {error}")
                return None
        return all_files
    
    def get_download_link(self, item):
        return f"https://drive.google.com/uc?export=download&id={item['id']}" if item['mimeType'].startswith('application/') else None
    
    def load_checkpoint(self):
        checkpoint_file = "processed_files.json"
        try:
            with open(checkpoint_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_checkpoint(self, processed_files):
        checkpoint_file = "processed_files.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(processed_files, f)

    def run_ETL(self, folder_link):
        processed_files = self.load_checkpoint()
        folder_id = self.extract_folder_id(folder_link)
        service = self.get_google_drive_service()
        folder_contents = self.get_folder_contents(service, folder_id)

        if folder_contents:
            print(f"Found {len(folder_contents)} PDF files in the specified folder.")
            for i,item in enumerate(folder_contents):
                print(f"{i+1} ---> Processing: {item['name']}")
                file_name = item['name']
                file_id = item['id']
                file_path = file_name
                file_path = file_path.rstrip()  # Remove trailing spaces
                # Add this line to ensure the file_path ends with .pdf before downloading
                if not file_path.endswith('.pdf'):          
                    file_path += '.pdf' 

                if file_id in processed_files:
                    print(f"Skipping processed file: {file_name}")
                    continue  # Skip to the next file

                print(f"Downloading: {file_name}")
                self.download_file(service, file_id, file_path)
                print(f"Downloaded: {file_name}")

                parts = file_name.split('/')
                destination = parts[-2] if len(parts) > 1 else ""
                title = os.path.splitext(parts[-1])[0]

                print(f"Performing OCR on: {file_name}")
                text = self.gemini_ocr(file_path)
                time.sleep(30)

                print(f"Updating Google Sheet with: {file_name}")
                self.update_google_sheet(destination, title, text)
                
                processed_files[file_id] = True  # Mark the file as processed
                self.save_checkpoint(processed_files)  # Save the checkpoint
                
                try:
                    os.remove(file_path)
                except PermissionError:
                    try:
                        time.sleep(1)
                        os.remove(file_path)
                    except PermissionError: 
                        os.unlink(file_path)
        else:
            print("No PDF files found in the specified folder.")


    # VIEW FOLDER CONTENTS

    def get_folder_details(self, folder_link, credentials_file):
        """Retrieves share links and item counts for all folders within the specified Google Drive folder."""
        folder_id = self.extract_folder_id(folder_link)
        
        # Authenticate and build the Drive API service
        scopes = ['https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scopes)
        service = build('drive', 'v3', credentials=credentials)

        # Query for subfolders
        query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
        results = service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
        folders = results.get('files', [])

        folder_details = []
        for folder in folders:
            folder_id = folder['id']

            # Query for items within the folder
            query = f"'{folder_id}' in parents"
            results = service.files().list(q=query, fields="files(id)").execute()
            item_count = len(results.get('files', []))

            folder_details.append((folder['name'], folder['webViewLink'], item_count))

        return folder_details

    def extract_folder_id(self, url):
        """Extracts the folder ID from a Google Drive URL."""
        pattern = r"folders/([A-Za-z0-9_-]+)\?"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def view_folder_details(self,
                             folder_link = "https://drive.google.com/drive/folders/103epRgaKBSrXuLI7dhnfVLPs4d3bj94o?usp=drive_link" ,
                             credentials_file = "smart-platform.json"):
        folder_details = self.get_folder_details(folder_link, credentials_file)
        folder_details_dict = {}
        for name, link, count in folder_details:
            folder_details_dict[name] = link
            print(f"Folder Name: {name}, Share Link: {link}, Item Count: {count}")
        
        return folder_details_dict
