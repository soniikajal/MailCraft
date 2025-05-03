import os
import csv
import time
import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import date

# Configuration
SENDER_EMAIL = "kish.kalakritii@gmail.com"
BUSINESS_NAME = "Kish Kalakriti"
BUSINESS_PHONE = "+91-7827044075"
BUSINESS_EMAIL = "kish.kalakritii@gmail.com"
BUSINESS_WEBSITE = "https://kishkalakriti.netlify.app"
BUSINESS_SOCIAL = "https://www.instagram.com/kish.kalakriti"
ATTACHMENT_PATH = None # Optional path to PDF attachment
SUBSCRIBERS_CSV = "subscribers.csv"
TEMPLATE_FILE = "newsletter.html"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

def get_gmail_service():
    """Authenticate and create a Gmail API service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_info(json.loads(open(TOKEN_FILE).read()), SCOPES)
    
    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def load_html_template(template_file):
    """Load HTML template from file."""
    try:
        with open(template_file, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Warning: Template file {template_file} not found.")
        return None

def create_newsletter_content(template_type):
    """Create content for different newsletter types."""
    if template_type == "welcome":
        return """
<ul>
    <li>Our <strong>website is now live!</strong> Visit us at <a href="https://kishkalakriti.netlify.app">kishkalakriti.netlify.app</a> to explore our full collection.</li>
    <li>Connect with us on <a href="https://www.linkedin.com/company/kish-kalakriti/"> LinkedIn </a> for business updates and behind-the-scenes content.</li>
    <li>Our popular <strong>customized chocolates</strong> are back in stock! Perfect for gifting or treating yourself.</li>
</ul>
"""
    elif template_type == "promotion":
        return """
<ul>
    <li>Enjoy 20% off on all handcrafted items this week only!</li>
    <li>Use code HANDMADE20 at checkout</li>
    <li>Free shipping on orders over ₹1000</li>
</ul>
"""
    elif template_type == "update":
        return """
<ul>
    <li>We've expanded our collection of handmade home decor</li>
    <li>New sustainable materials are now being used in our jewelry line</li>
    <li>Our website has been updated with improved shopping features</li>
    <li>Extended business hours to serve you better</li>
</ul>
"""
    else:  # Default newsletter content
        return """
<ul>
    <li>New summer-inspired home decor pieces have arrived</li>
    <li>Limited edition handcrafted jewelry collection now available</li>
    <li>Custom gift options for upcoming celebrations</li>
</ul>

<h3 class="section-title">Upcoming Events</h3>
<ul>
    <li>Artisan showcase on June 15th</li>
    <li>Special discount week starting May 10th</li>
    <li>New seasonal collection preview</li>
</ul>
"""

def create_html_email_content(subscriber_name, template_type):
    """Create HTML email content using the template."""
    html_template = load_html_template(TEMPLATE_FILE)
    
    # Get current date formatted as "Month Day, Year"
    current_date = date.today().strftime('%B %d, %Y')
    
    # Use a fallback if name is missing or empty
    if not subscriber_name or subscriber_name.strip() == '':
        subscriber_name = "Craft Enthusiast"
    
    if not html_template:
        # Fallback to basic HTML if template not found
        return f"""
        <html>
        <body>
            <h1>{BUSINESS_NAME}</h1>
            <p>Dear {subscriber_name},</p>
            <p>Thank you for subscribing to our newsletter!</p>
            {create_newsletter_content(template_type)}
            <p>Best regards,<br>{BUSINESS_NAME} Team</p>
            <p>To unsubscribe, please reply with 'UNSUBSCRIBE' in the subject line.</p>
        </body>
        </html>
        """
    
    # Replace placeholders in the template
    content = create_newsletter_content(template_type)
    
    html_content = html_template.replace("{{SUBSCRIBER_NAME}}", subscriber_name)
    html_content = html_content.replace("{{BUSINESS_NAME}}", BUSINESS_NAME)
    html_content = html_content.replace("{{CONTENT}}", content)
    html_content = html_content.replace("{{BUSINESS_PHONE}}", BUSINESS_PHONE)
    html_content = html_content.replace("{{BUSINESS_EMAIL}}", BUSINESS_EMAIL)
    html_content = html_content.replace("{{BUSINESS_WEBSITE}}", BUSINESS_WEBSITE)
    html_content = html_content.replace("{{BUSINESS_SOCIAL}}", BUSINESS_SOCIAL)
    html_content = html_content.replace("{{CURRENT_DATE}}", current_date)
    
    return html_content

def create_email(to, subject, html_content, attachment_path=None):
    """Create an email with HTML content and optional attachment."""
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['subject'] = subject
    
    # Create plain text version as fallback
    plain_text = "This email contains HTML content that your email client doesn't support."
    part1 = MIMEText(plain_text, 'plain')
    part2 = MIMEText(html_content, 'html')
    
    # Attach parts in order: plain text, then HTML
    message.attach(part1)
    message.attach(part2)
    
    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as file:
            attachment = MIMEApplication(file.read(), _subtype='pdf')
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
            message.attach(attachment)
    
    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_string().encode()).decode()
    return {'raw': raw_message}

def send_email(service, email_message):
    """Send an email using Gmail API."""
    try:
        message = service.users().messages().send(userId='me', body=email_message).execute()
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def main():
    print(f"Starting email campaign for {BUSINESS_NAME}...")

    # Check if subscribers CSV exists
    if not os.path.exists(SUBSCRIBERS_CSV):
        print(f"Error: Subscribers CSV file not found at {SUBSCRIBERS_CSV}")
        print("Please ensure your subscribers CSV file is in the correct location and try again.")
        return

    # Check if HTML template exists
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Warning: HTML template file not found at {TEMPLATE_FILE}")
        proceed = input("Continue with basic HTML template? (y/n): ").lower() == 'y'
        if not proceed:
            return

    # Check if attachment exists (if specified)
    if ATTACHMENT_PATH and not os.path.exists(ATTACHMENT_PATH):
        print(f"Warning: Attachment file not found at {ATTACHMENT_PATH}")
        proceed = input("Continue without attachment? (y/n): ").lower() == 'y'
        if not proceed:
            return

    try:
        # Initialize the Gmail API service
        service = get_gmail_service()

        # Read subscribers from CSV file
        subscribers = []
        with open(SUBSCRIBERS_CSV, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                subscribers.append(row)

        total_subscribers = len(subscribers)
        print(f"Found {total_subscribers} subscribers in the CSV file")

        # Select email template type
        print("\nSelect the type of email to send:")
        print("1. Welcome")
        print("2. Newsletter")
        print("3. Promotion")
        print("4. Update")
        template_choice = input("Enter your choice (1-4): ")

        template_mapping = {
            "1": "welcome",
            "2": "newsletter",
            "3": "promotion",
            "4": "update"
        }

        template_type = template_mapping.get(template_choice, "newsletter")

        # Customize subject line
        default_subjects = {
            "welcome": f"Welcome to {BUSINESS_NAME} - Handcrafted with Love",
            "newsletter": f"{BUSINESS_NAME} - Handcrafted Newsletter",
            "promotion": f"Special Offer on Handmade Treasures from {BUSINESS_NAME}",
            "update": f"Updates from {BUSINESS_NAME} - Handcrafted with Love"
        }

        suggested_subject = default_subjects.get(template_type)
        custom_subject = input(f"Enter email subject (default: '{suggested_subject}'): ")
        subject = custom_subject if custom_subject else suggested_subject

        # Option to send test email first
        test_mode = input("\nWould you like to send a test email to yourself first? (y/n): ").lower() == 'y'
        if test_mode:
            test_email = input("Enter your email address for the test: ")
            print("Sending test email...")
            
            # Create test HTML content
            test_subscriber = subscribers[0] if subscribers else {"name": "Valued Customer"}
            test_html_content = create_html_email_content(
                test_subscriber.get('name', 'Valued Customer'),
                template_type
            )
            
            # Create subject line for test
            test_subject = f"TEST - {subject}"
            
            # Create email
            test_email_obj = create_email(test_email, test_subject, test_html_content, ATTACHMENT_PATH)
            
            # Send test email
            test_result = send_email(service, test_email_obj)
            
            if test_result:
                print("Test email sent successfully!")
                proceed = input("Would you like to proceed with sending emails to all subscribers? (y/n): ").lower() == 'y'
                if not proceed:
                    print("Campaign cancelled. No emails were sent to subscribers.")
                    return
            else:
                print("Failed to send test email. Please check your configuration and try again.")
                return

        # Confirm before sending to all subscribers
        if not test_mode:
            confirm = input(f"Are you sure you want to send emails to {total_subscribers} subscribers? (y/n): ").lower() == 'y'
            if not confirm:
                print("Campaign cancelled. No emails were sent.")
                return

        # Counter for sent emails
        sent_count = 0
        failed_count = 0
        failed_emails = []

        # Ask for batch size to avoid rate limiting
        batch_size = int(input("How many emails would you like to send in each batch? (recommended: 25): ") or "25")
        delay_between_batches = int(input("How many seconds would you like to wait between batches? (recommended: 300): ") or "300")

        # Process each subscriber in batches
        for i, subscriber in enumerate(subscribers):
            subscriber_email = subscriber.get('email', '').strip()
            if not subscriber_email:
                print(f"Skipping subscriber at row {i+1} - no email address found")
                failed_count += 1
                continue

            subscriber_name = subscriber.get('name', 'Valued Customer')
            
            print(f"Processing email to {subscriber_email} ({i+1}/{total_subscribers})...")
            
            # Create HTML content
            html_content = create_html_email_content(subscriber_name, template_type)
            
            # Create email
            email = create_email(subscriber_email, subject, html_content, ATTACHMENT_PATH)
            
            # Send email
            result = send_email(service, email)
            
            if result:
                sent_count += 1
                print(f"✓ Email sent to {subscriber_email} ({sent_count}/{total_subscribers})")
            else:
                failed_count += 1
                failed_emails.append(subscriber_email)
                print(f"✗ Failed to send email to {subscriber_email}")
            
            # Add a small delay between emails to avoid rate limits
            time.sleep(2)
            
            # Add a larger delay between batches
            if (i + 1) % batch_size == 0 and i + 1 < total_subscribers:
                print(f"\nCompleted batch of {batch_size} emails. Waiting for {delay_between_batches} seconds before sending the next batch...")
                for remaining in range(delay_between_batches, 0, -10):
                    print(f"Resuming in {remaining} seconds...", end="\r")
                    time.sleep(10)
                print("\nResuming email campaign...\n")

        print("\n=== Campaign Summary ===")
        print(f"Successfully sent {sent_count} out of {total_subscribers} emails.")
        
        if failed_count > 0:
            print(f"Failed to send {failed_count} emails to the following subscribers:")
            for email in failed_emails:
                print(f"- {email}")
            print("\nYou may want to try sending emails to these subscribers manually.")
        
        print("\nCampaign completed!")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

if __name__ == '__main__':
    main()
