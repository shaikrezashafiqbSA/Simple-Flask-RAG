# smart-travels
## README: smart-travels - Retrieval Augmented Generation for Travelers

This repository provides a Proof of Concept (POC) implementation of an AI travel itinerary generator. The RAG model is designed to assist travelers by generating creative text formats, like travel itineraries or trip descriptions, based on user prompts and retrieved information from the "Master Database" Google sheet.

**Getting Started:**
****
This guide covers the deployment and maintenance of the Smart Travels RAG application on an AWS EC2 instance. It assumes you have basic familiarity with Linux, Git, Python virtual environments, and AWS EC2.


1. **EC2 Instance Preparation**
   
   1. Create EC2 Instance: 
      1. In the AWS Management Console, launch a new EC2 instance. 
      ![](C:\PycharmProjects\smart-travels\readme\ec21.png)
      2. Name your instance. 
      ![](C:\PycharmProjects\smart-travels\readme\ec22.png)
      3. Select: Ubuntu Server 24.05 LTS (HVM), SSD Volume Type. 
      ![](C:\PycharmProjects\smart-travels\readme\ec23.png)
      4. Choose an appropriate instance type (e.g., t2.micro for development).
      ![](C:\PycharmProjects\smart-travels\readme\ec24.png)
      5. Select an existing key pair (backend-RAG.pem) or create a new one.
      ![](C:\PycharmProjects\smart-travels\readme\ec25.png)
      6. Use existing security group "launch-wizard-3".
      ![](C:\PycharmProjects\smart-travels\readme\ec26.png)
   2. SSH Connection and System Setup
      System updates
      ```bash
      sudo apt update
      sudo apt upgrade
      ```
      Make folder for backend path
      ```bash
      mkdir smartworld
      ls smartworld
      ```
      ```bash
      git clone https://github.com/calllevels/smart-travels
      ```
      ![](C:\PycharmProjects\smart-travels\readme\ec2_2.png)

   3. Elastic IP (Optional): Allocate and associate an EIP for a static IP.

2. **Project setup**
   0. Connect to instance
      ![](C:\PycharmProjects\smart-travels\readme\ec27.png)
   1. Git deployment
      1. Generate an SSH key pair on the EC2 instance:asd
      ```bash
      ssh-keygen -t ed25519 -C 'dev@SWTT.com'
      ```
      Then copy and add public key to your Git provider.
      2. Or given access to smart-world repository, use your git username and Personal Access Token in place of password
      
   2. Environment setup and dependencies
      ```bash
      sudo apt install python3-pip 
      sudo apt install python3.12-venv    
      python3 -m venv myenv    
      source myenv/bin/activate
      pip3 install -r requirements.txt
      ```
   3. .env variables
      1. Google Gemini API Key 
         1. Create a Google Cloud Project:
            1. If you don't have one, go to the Google Cloud Console and create a new project.
         2. Enable the Gemini API:
            1. In the Cloud Console, go to "APIs & Services" > "Library".
            2. Search for "Gemini API" and click on it. 
            3. Click "Enable" (if it's not already enabled). 
         3. Create Credentials:
            1. Go to "APIs & Services" > "Credentials". 
            2. Click "Create Credentials" > "API key". 
            3. This will generate an API key. Copy and save it securely. 
         4. Set Environment Variable (Optional):
            1. In your project's environment (or a .env file), you can set:
            2. GEMINI_API_KEY = "your_gemini_api_key"
   4. Obtaining a Google Sheets API Key Using a Service Account JSON File
      1. To interact with Google Sheets programmatically, you'll need an API key. This guide explains how to obtain one using a service account JSON file:
         1. Create a Service Account:
         2. Go to the Google Cloud Console: Make sure you have a Google Cloud project or create a new one. 
         3. Navigate to IAM & Admin > Service Accounts: Click "Create Service Account". 
         4. Fill in details: Give your service account a descriptive name and click "Create and Continue". 
         5. Grant permissions: Select "Basic > Editor" role and click "Continue". 
         6. Grant users access (optional): Skip this step and click "Done".
      2. Create a JSON Key:
         1. In the Service Accounts list, click on the email address of your newly created account.
         2. Go to the Keys tab and click "Add Key" > "Create new key".
         3. Choose "JSON" as the key type and click "Create". This downloads a JSON file to your computer.
      3. Enable the Google Sheets API:
         1. In the Google Cloud Console, navigate to APIs & Services > Enabled APIs & Services. 
         2. Click "+ ENABLE APIS AND SERVICES" and search for "Google Sheets API". 
         3. Click on the API and click "Enable".
      4. Share Your Google Sheet:
         1. Open the Google Sheet you want to access. 
         2. Click the "Share" button in the top right corner. 
         3. Share the sheet with the email address of your service account (found in the JSON file). 
         4. Grant it "Editor" permissions.
      5. Using the JSON Key in Your Code:
         1. Store the JSON file as "smart-platform.json" in the main repo.
         2. This will be access by the POC codes for access to your google sheet
3. ETL Bot Boto3 Keys (AWS IAM)
   1. Create an IAM User:
      1. Log in to your AWS Management Console.
      2. Navigate to the IAM (Identity and Access Management) service.
      3. Click on "Users" and then "Add users".
      4. Provide a username (e.g., "ETL_BOT") and select "Programmatic access".
      5. Click "Next: Permissions".
   2. Set Permissions:
      1. Choose "Attach existing policies directly".
      2. Search for and select "AmazonS3FullAccess" (or a more restricted policy if your ETL job doesn't require full access).
      3. Click "Next: Tags" (you can skip adding tags if you don't need them).
      4. Click "Next: Review" and then "Create user".
   3. Get Access and Secret Keys:
      1. On the final screen, you'll see the "Access key ID" and have an option to reveal the "Secret access key".
      2. Make sure to save these values securely. You won't be able to retrieve the secret key again later.
   4. Configure Environment Variables:
      1. In your project's environment (or a .env file), set the following:
      2. ETL_BOT_BOTO3_ACCESS_KEY = "your_access_key_id"
      3. ETL_BOT_BOTO3_SECRET_KEY = "your_secret_access_key"
   



4. **Running and updating the application**
   1. to run the app_POC.py persistently in the background, use nohup:
   ```bash
   no hup python3 app_POC.py &
   ```
   This will redirect output to nohup.out. To monitor logs:
   ```bash
   tail -f nohup.out
   ```
   ![](C:\PycharmProjects\smart-travels\readme\ec2_2.png)






