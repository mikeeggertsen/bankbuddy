import os
from twilio.rest import Client 
from django.core.mail import send_mail
 
account_sid = 'AC3421f05af30e4e64561f6f8f19e785b1' 
auth_token = os.environ["SMS_API_TOKEN"]
client = Client(account_sid, auth_token) 

def send_sms(msg_content, phone):
    client.messages.create(  
        messaging_service_sid='MG8e80b1d634a6911c2f55ef8daa3d63db', 
        body=msg_content,      
        to=f"+45{str(phone)}" 
) 


def send_email(subject, message, recepient):
    send_mail(
    subject,
    message,
    'kontakt@mikeeggertsen.com',
    [recepient],
    fail_silently=False,
)
 