# scraper/utils.py

from twilio.rest import Client
from django.conf import settings

def send_text_notification(message_body):
    """
    Sends an SMS notification using Twilio with a single message body.
    """
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    messaging_service_sid = settings.TWILIO_MESSAGING_SERVICE_SID
    to_number = settings.NOTIFICATION_PHONE_NUMBER
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        body=message_body,
        to=to_number
    )
    return message.sid