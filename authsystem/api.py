import requests
import os

def send_sms(to_phone, message):
    url_tuple = os.environ['SMS_API_URL'],
    url = url_tuple[0]
    api_key_tuple = os.environ['SMS_API_KEY'],
    api_key = api_key_tuple[0]
    data = {
        to_phone,
        message,
        api_key,
    }
    print(f"SMS SENT: {message}")
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f'Failed to send sms verification code: {e}')