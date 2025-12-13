import os
import smtplib
import logging
from flask import Flask, request, jsonify # Changed from fastapi
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize Flask instead of FastAPI
app = Flask(__name__)

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SMTP_SERVER = 'smtp.gmail.com' # Hardcoded for clarity
SMTP_PORT = 587
SMTP_TIMEOUT = 10

@app.route("/", methods=["POST"]) # Flask route definition
def send_email():
    # In Flask, we get JSON data from request.json
    data = request.json
    
    # Extract fields manually (No Pydantic validation in basic Flask)
    to_email = data.get('to')
    subject = data.get('subject')
    text_content = data.get('text')
    html_content = data.get('html')

    if not to_email or not subject:
        return jsonify({"error": "Missing 'to' or 'subject'"}), 400

    sender_email = os.getenv('MAIL_USERNAME')
    sender_password = os.getenv('MAIL_PASSWORD')

    if not sender_email or not sender_password:
        return jsonify({"error": "Server misconfiguration: missing credentials"}), 500

    # Create Message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    if html_content:
        msg.attach(MIMEText(html_content, "html"))
    elif text_content:
        msg.attach(MIMEText(text_content, "plain"))
    else:
        return jsonify({"error": "No message body provided"}), 400

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
            server.starttls() # Required for Gmail
            server.login(sender_email, sender_password)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to_email}")
        return jsonify({"success": True, "message": "Email sent"}), 200

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return jsonify({"error": str(e)}), 500

