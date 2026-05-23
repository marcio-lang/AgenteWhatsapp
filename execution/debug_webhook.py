import requests
import os
from dotenv import load_dotenv

load_dotenv()

URL = "http://10.0.4.119:8080/webhook/set/chat"
API_KEY = "429683C4C977415CAAFCCE10F7D57E11"

payload = {
    "webhookUrl": "http://10.0.4.74:3000/webhook",
    "enabled": True,
    "events": ["MESSAGES_UPSERT"]
}

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

print(f"POSTing to {URL}")
payload_v3 = {
    "webhook": {
        "url": "http://10.0.4.74:3000/webhook",
        "enabled": True,
        "events": ["MESSAGES_UPSERT"]
    }
}

try:
    r = requests.post(URL.replace('find', 'set'), json=payload_v3, headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Content: {r.text}")
except Exception as e:
    print(f"Error: {e}")
