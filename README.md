
# README: Simple RAG POC

This repository provides a Proof of Concept (POC) implementation of an genAI content generation by fetching data from a google sheet table. 

**Getting Started:**
****
This guide covers the deployment and maintenance of a simple RAG on an AWS EC2 instance and accessing API endpoints 


1. **EC2 Instance Preparation**
   
   1. Create EC2 Instance: 
      1. In the AWS Management Console, launch a new EC2 instance. 
      ![](images/ec21.png)
      2. Name your instance.

      3. Select: Ubuntu Server 24.05 LTS (HVM), SSD Volume Type. 
      ![](images/ec23.png)
      4. Choose an appropriate instance type (e.g., t2.micro for development).
      ![](images/ec24.png)
      5. Select an existing key pair (backend-RAG.pem) or create a new one.
      ![](images/ec25.png)
      6. Use existing security group "launch-wizard-3".
      ![](images/ec26.png)
   2. SSH Connection and System Setup
      System updates
      ```bash
      sudo apt update
      sudo apt upgrade
      ```
      Make folder for backend path
      ```bash
      mkdir simple-RAG
      ls simple-RAG
      ```
      ```bash
      git clone https://github.com/shaikrezashafiqbSA/Simple-RAG.git
      ```
      
      ![](images/ec2_2.png)

   4. Elastic IP (Optional): Allocate and associate an EIP for a static IP.

2. **Project setup**
   Connect to instance
   
   ![](images/ec27.png)

   2. Git deployment
      1. Generate an SSH key pair on the EC2 instance:asd
      ```bash
      ssh-keygen -t ed25519 -C 'dev@gmail.com'
      ```
      Then copy and add public key to your Git provider.
      2. Or given access to simple-RAG repository, use your git username and Personal Access Token in place of password
      
   3. Environment setup and dependencies
      ```bash
      sudo apt install python3-pip 
      sudo apt install python3.12-venv    
      python3 -m venv myenv    
      source myenv/bin/activate
      pip3 install -r requirements.txt
      ```
   4. .env variables
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
   5. Obtaining a Google Sheets API Key Using a Service Account JSON File
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
         1. Store the JSON file as "GCP.json" in the main repo.
         2. This will be access by the POC codes for access to your google sheet
   6. ETL Bot Boto3 Keys (AWS IAM)
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
6. Updating and Restarting 
   1. Stop the Process:
      1. Find the process ID (PID) using ps aux | grep app_POC.py. 
      2. Kill the process: kill <PID>
      3. Update Code: Pull the latest changes from your Git repository:
      ```Bash
      git pull
      ```
   2. Check for Errors: Review the code, especially if it's a Flask app, for:
      1. Duplicate function definitions 
      2. Indentation issues 
      3. Typos 
      4. Missing imports 
      5. Restart: Run the application with nohup as before.
7. Reverse Proxy (Optional)
   1. Reverse Proxy: Nginx acts as a reverse proxy, sitting in front of your Flask app. It receives requests from clients (like Postman) and forwards them to your app.
   2. Virtual Hosts: Nginx can host multiple websites or services on a single server using virtual hosts. Each virtual host has its own configuration, allowing you to map different domains or URLs to different applications.
   3. URL Rewriting: Nginx can modify the incoming request URLs before passing them to your backend. This allows you to create user-friendly or shorter URLs.
   4. Steps to Configure Nginx 
      1. Install and Start Nginx: If you haven't already, follow the steps from our previous discussions to install and start Nginx on your EC2 instance. 
      2. Create a Virtual Host Configuration File:
      3. Open a terminal on your EC2 instance. 
      4. Navigate to the sites-available directory:
      ```Bash
      cd /etc/nginx/sites-available
      ```
      5. Create a new file for your virtual host configuration (e.g., test.com):
      ```Bash
      sudo nano test.com  
      ```
      6. Add the Configuration:
      ```Nginx
      server {
              listen 80;         # Listen on port 80 (HTTP)
              listen 443 ssl;    # Listen on port 443 (HTTPS) if using SSL
              server_name test.com;    # Your custom domain name

              location /api {      # Match requests to /api
        rewrite ^/api(.*) /$1 break; # Remove /api from the URL
        proxy_pass http://127.0.0.1:5000/api/2;   # Forward to Flask
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
       }
      }
   
   5. Explanation:
      1. listen 80;: Listens for incoming HTTP traffic.
      2. listen 443 ssl;: Listens for incoming HTTPS traffic if you have an SSL certificate.
      3. server_name test.com;: The domain you want to use (replace test.com with your actual domain).
      4. location /api { ... }: This block matches all requests starting with "/api".
      5. rewrite ^/api(.*) /$1 break;: This line removes "/api" from the URL.
      6. proxy_pass http://127.0.0.1:5000/api/2;: This line forwards the modified request to your Flask app running on the local address 127.0.0.1:5000 at the path /api/2.
      7. The rest of the location block configures additional headers for the proxy.
      8. Enable the Virtual Host:
      ```Bash
      sudo ln -s /etc/nginx/sites-available/test.com /etc/nginx/sites-enabled/
      ```

   6. Test and Restart Nginx:
   ```Bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

8. Accessing Your API:
   1. Assuming NGINX instructions was followed (else use public IP from EC2 description), you should be able to access the following API endpoints
      1. POST: https://test.com/api/2 - produces curated itinerary
         ```bash 
         body: {"prompt": "i want to go pahang for 4 days, for 2 pax"} 
         ```
      2. POST: https://test.com/api/3 - streaming version of api/2
      3. GET: https://test.com/api/get_itinerary/1719210530593755200x 
         1. This will fetch a historical itinerary from the "Master Database" google sheets, "prompts" sheet given a timestamp id string eg: 1719210530593755200x
      4. GET: https://test.com/api/ingest
         This endpoint will populate the "Master Database" google sheets, "inventory" sheet with Gemini image analyses (OCR prompt) from a given folder_link
            ```bash
            body: {"folder_link":"1pRG5W1oJEc8Ify3XQ0iWY1NXM-63FzhN?usp=drive_link"}
            ```
   2. Key points
      1. Replace placeholders with your actual values (domain, IP address, etc.). 
      2. If you want to use HTTPS, you'll need to obtain and configure an SSL certificate for your domain. 
      3. Ensure your security group allows traffic on the ports you're using. 
      4. Public Access: If you want to make your API accessible to the public via https://test.com/api, then you would need to register the domain test.com with a domain registrar and configure DNS settings to point it to your EC2 instance's public IP address or Elastic IP. 
      5. HTTPS: If you want to use HTTPS (the https:// protocol), you'll need a valid SSL certificate for the domain test.com. You can obtain free SSL certificates from services like Let's Encrypt.






