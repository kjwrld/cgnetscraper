# scraper/utils.py

from twilio.rest import Client
from django.conf import settings

def send_text_notification(title, price, link):
    """
    Sends an SMS notification using Twilio.
    """
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    messaging_service_sid = settings.TWILIO_MESSAGING_SERVICE_SID
    to_number = settings.NOTIFICATION_PHONE_NUMBER
    client = Client(account_sid, auth_token)
    
    # Build the message body
    message_body = (
        f"New Classified Ad Alert!\n"
        f"Title: {title}\n"
        f"Price: {price}\n"
        f"Link: {link}"
    )
    
    # Ensure you have configured these in your settings.py or environment variables.
    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        body=message_body,
        to=settings.NOTIFICATION_PHONE_NUMBER
    )
    return message.sid