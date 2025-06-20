#!/usr/bin/env python3

import os
import random
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('../../../.env')

# Email configuration
SMTP_SERVER = os.getenv('SMTP_HOST', 'mailhog')
SMTP_PORT = int(os.getenv('SMTP_PORT', 1025))
SENDER_EMAIL = os.getenv('BOT_EMAIL', 'bot@local')
RECIPIENT_EMAIL = os.getenv('LLM_EMAIL', 'llm@local')

# Sample application requests
APP_REQUESTS = [
    "Create a simple web dashboard using Node.js and Express that displays system metrics.",
    "Generate a Python script that processes CSV files and generates a report with statistics.",
    "Build a REST API with FastAPI that manages a todo list with CRUD operations.",
    "Create a React frontend with a form that collects user feedback and saves it to a JSON file.",
    "Generate a Python script that monitors a directory for new files and processes them.",
    "Build a simple chat application using WebSockets with Python backend and JavaScript frontend.",
    "Create a data visualization dashboard using Plotly and Dash that loads data from a CSV file.",
]

def send_email(subject, body):
    """Send an email with the given subject and body."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {RECIPIENT_EMAIL}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def generate_random_request():
    """Generate a random application request."""
    return random.choice(APP_REQUESTS)

def main():
    logger.info("Bot generator started")
    
    try:
        while True:
            # Generate a random request
            request = generate_random_request()
            
            # Send the request as an email
            subject = "text2app: New Application Request"
            body = f"""
            Hello LLM,
            
            Please generate an application with the following requirements:
            
            {request}
            
            Please respond with a .eml file containing the application.
            
            Best regards,
            Bot
            """
            
            logger.info(f"Sending request: {request}")
            send_email(subject, body)
            
            # Wait for 1 minute before sending the next request
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Bot generator stopped by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
