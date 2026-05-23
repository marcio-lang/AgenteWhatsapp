import requests
import json

url = "http://localhost:3000/webhook"

# Mock payload mocking what Evolution sends
payload = {
    "data": {
        "key": {
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": False
        },
        "message": {
            "conversation": "1"
        }
    }
}

print(f"Sending test payload to {url}...")
# Bypass proxy for localhost
session = requests.Session()
session.trust_env = False

try:
    r = session.post(url, json=payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
