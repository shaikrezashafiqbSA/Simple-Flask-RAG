import os
import re
import logging
import requests
import pandas as pd
from io import BytesIO
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from llm_handler.GHandler import GHandler
import boto3
# import pytesseract
import PyPDF2
from telegram import BotCommand
# Configuration and Constants
from settings import TELEGRAM_TRAVELLER_API_KEY, SHEET_NAME#, GOOGLE_DRIVE_FOLDER_ID, S3_BUCKET_NAME
from settings import GEMINI_API_KEY1 as GEMINI_API_KEY
# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize Google Sheets and Drive API
credentials = Credentials.from_service_account_file('smart-platform.json', scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets'])
drive_service = build('drive', 'v3', credentials=credentials)
sheet_service = build('sheets', 'v4', credentials=credentials)

# Initialize S3 client
s3_client = boto3.client('s3')




# Function to sanitize file names
def sanitize_file_name(caption):
    return re.sub(r'[^a-zA-Z0-9\s\-_\.]', '_', caption)

# Function to upload file to Google Drive
def upload_to_google_drive(file_path, folder_id, file_name):
    try:
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except Exception as e:
        logging.error(f"Error uploading file to Google Drive: {e}")
        return None

# Function to upload file to S3
def upload_to_s3(file_path, bucket_name, object_name=None):
    try:
        s3_client.upload_file(file_path, bucket_name, object_name or os.path.basename(file_path))
    except Exception as e:
        logging.error(f"Error uploading file to S3: {e}")

# Function to extract text from PDF using PyPDF2
def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfFileReader(f)
            text = ""
            for page_num in range(reader.numPages):
                page = reader.getPage(page_num)
                text += page.extract_text()
            return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return ""

# Function to extract text from images using Tesseract OCR
def extract_text_from_image(file_path):
    try:
        prompt_1 = "You are an OCR bot. Extract ALL the text from the image as raw text. Ensure all pricing, phone numbers and emails are extracted ACCURATELY. OCR text output is sometimes wrong, so correct it where needed."
        g_handler = GHandler(GEMINI_API_KEY,                  
                    generation_config = {"temperature": 0.95,
                                        "top_p": 0.95,
                                        "top_k": 40,
                                        # "max_output_tokens": 2048,
                                        },
                    block_threshold="BLOCK_NONE",
                    )
        prompt_2 = None #"Reorganise the OCR output into an easy to read format, with sections "
        g_response = g_handler.prompt_image(model_name = "gemini-pro-vision",
                                    image_path = file_path,
                                    prompt_1 = prompt_1,
                                    prompt_2 = prompt_2,
                                            )
        try:
            llm_response_text = g_response.text
            return llm_response_text
        except Exception as e: 
            llm_response_text = f"Error: {str(e)}\nSomething went wrong with the LLM model. Please try again."
    except Exception as e:
        logging.error(f"Error extracting text from image: {e}")
        return ""

# Function to update Google Sheets
def update_google_sheet(data, sheet_name, worksheet_name):
    try:
        df = pd.DataFrame(data)
        body = {
            'values': df.values.tolist()
        }
        sheet_service.spreadsheets().values().append(
            spreadsheetId=sheet_name,
            range=worksheet_name,
            valueInputOption='RAW',
            body=body
        ).execute()
    except Exception as e:
        logging.error(f"Error updating Google Sheet: {e}")

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
    I'm a bot that can help you digitize your travel content. 
    Input: "SHEET_NAME - meta_data" and upload an image or PDF file.
    Example: "partners - perlis_river_adventure 2024-08 by Puan Siti"
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.effective_chat.type
    process_image = chat_type == "private" or (
        chat_type in ["group", "supergroup"] and any(
            mention.user.id == context.bot.id for mention in update.message.entities
        )) or (update.message.reply_to_message and update.message.reply_to_message.from_user.is_bot) or (
        update.message.entities and any(ent.type == "mention" for ent in update.message.entities))

    if not process_image:
        return

    caption = update.message.caption or ""
    table_name, meta_data = caption.split(" - ")
    sanitized_caption = sanitize_file_name(caption)

    file_info = None
    file_extension = None
    if update.message.document:
        file_info = update.message.document
        file_extension = file_info.file_name.split('.')[-1].lower()
    elif update.message.photo:
        file_info = update.message.photo[-1]
        file_extension = 'jpg'

    if not file_info:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I can only process images and PDF files!")
        return

    file = await context.bot.get_file(file_info.file_id)
    file_path = os.path.join("./database/telegram/", update.effective_message.document.file_name if file_extension == 'pdf' else f"{sanitized_caption}.jpg")
    response = requests.get(file.file_path)
    with open(file_path, "wb") as f:
        f.write(response.content)

    if file_extension == 'pdf':
        text = f"PDF file ({update.effective_message.document.file_name}) received\n ---> processing..."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        llm_response_text = extract_text_from_pdf(file_path)

        # Upload to Google Drive and S3
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Uploading to Google Drive and S3...")
        # upload_to_google_drive(file_path, GOOGLE_DRIVE_FOLDER_ID, update.effective_message.document.file_name)
        # upload_to_s3(file_path, S3_BUCKET_NAME, update.effective_message.document.file_name)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=llm_response_text)
    elif file_extension in ['jpg', 'jpeg', 'png']:
        try:
            text = f"Image ({caption}) received\n ---> processing..."
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

            img = Image.open(BytesIO(response.content))
            llm_response_text = extract_text_from_image(file_path)

            # Upload to Google Drive and S3
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Uploading to Google Drive and S3...")
            # upload_to_google_drive(file_path, GOOGLE_DRIVE_FOLDER_ID, sanitized_caption)
            # upload_to_s3(file_path, S3_BUCKET_NAME, sanitized_caption)

            await context.bot.send_message(chat_id=update.effective_chat.id, text=llm_response_text)
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Sorry, something went wrong! Error Message:\n{e}\n--->Please try again.")
            return
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I can only process images and PDF files!")

    # Update Google Sheet
    data = [{"meta": meta_data, "data": llm_response_text}]
    update_google_sheet(data, SHEET_NAME, table_name)


async def set_commands(bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="pdf_handler", description="Handle PDF uploads"),
        BotCommand(command="image_handler", description="Handle image uploads"),
        BotCommand(command="etl_ingest", description="Ingest data for ETL process"),
        BotCommand(command="send_to_S3", description="Send files to S3"),
    ]
    await bot.set_my_commands(commands)

# Main function to run the bot
if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TRAVELLER_API_KEY).build()
    start_handler = CommandHandler('start', start)
    application.add_handler(CommandHandler('start', start))
    # application.add_handler(CommandHandler('etl_ingest', etl_ingest))
    # application.add_handler(CommandHandler('send_to_S3', send_to_S3))
    pdf_handler = MessageHandler(filters.Document.PDF, image_handler)
    img_handler = MessageHandler(filters.PHOTO, image_handler)

    application.add_handler(start_handler)
    application.add_handler(pdf_handler)
    application.add_handler(img_handler)

        # Set commands after the application has been initialized
    async def main():
        await set_commands(application.bot)

    application.run_polling(poll_interval=3, timeout=30, bootstrap_retries=-1, on_startup=[main])
