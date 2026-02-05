import imaplib
import email
from email.header import decode_header
import datetime
#import dateutil.parser
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_core.tools import tool

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER")


# Ensure the download folder exists
if not os.path.isdir(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@tool
def read_last_24h_emails() -> str:
    """Read last 24 hours emails from the inbox, download attachments."""
    try:
        print("Reading last 24 hours emails...")
        # 1. Connect to the server and log in
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        # 2. Calculate date for 24 hours ago
        since_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d-%b-%Y")
        
        # sent since last two hours (hours=2)
        # Calculate time threshold
        # time_threshold = datetime.datetime.now() - datetime.timedelta(hours=hours)

        # 3. Search for emails received since that date
        # '(SENTSINCE ...)' filters by date, '(UNSEEN)' can be added to get only unread
        status, messages = mail.search(None, f'(FROM "{SENDER_EMAIL}" SENTSINCE {since_date})')#'(UNSEEN)'
        
        if status != 'OK':
            print("No new emails found.")
            return

        mail_ids = messages[0].split()
        print(f"Found {len(mail_ids)} potential emails. Processing...")

        # 4. Fetch and display email details
        for mail_id in mail_ids:
            _, msg_data = mail.fetch(mail_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode Subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # Get Sender
                    from_ = msg.get("From")
                    date_ = msg.get("Date")
                    message_ = get_email_body(msg)

                    print(f"Date: {date_}")
                    print(f"From: {from_}")
                    print(f"Subject: {subject}")    
                    print(f"Message: {message_}")
                    print("-" * 20)
                
                download_attachments(msg)

                
        # 5. Close connection
        mail.close()
        mail.logout()

    except Exception as e:
        print(f"An error occurred: {e}")

    return "Emails read successfully"

def get_email_body(msg):
    """Recursively extract the plain text body from an email message object."""
    if msg.is_multipart():
        for part in msg.walk():
            # Skip any non-text parts or attachments
            if part.get_content_type() == 'text/plain' and 'attachment' not in str(part.get('Content-Disposition', '')):
                # Decode the payload and return it
                return part.get_payload(decode=True).decode('utf-8')
    else:
        # Not multipart, so it's a single part message
        return msg.get_payload(decode=True).decode('utf-8')
    return "" # Return empty string if no plain text body is found

def download_attachments(msg):
    try:
        # Walk through the parts of the email message
            for part in msg.walk():
                # Check if the part has a 'Content-Disposition' header with 'attachment'
                if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
                    filename = part.get_filename()
                    if filename:
                        # Sanitize filename (basic check for valid path characters is recommended)
                        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
                        
                        # Save the attachment file
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Downloaded attachment: {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")


#tools_by_name = {tool.name: tool for tool in tools}

mail_tools = [read_last_24h_emails]
mail_tools_by_name = {tool.name: tool for tool in mail_tools}

if __name__ == "__main__":
    read_last_24h_emails()
