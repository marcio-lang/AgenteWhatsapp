import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Fixed URL construction
API_URL = os.getenv("EVOLUTION_API_URL").split("/instance/")[0]
API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE = "chat"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def check_jid(jid):
    print(f"\n=== Checking {jid} ===")
    
    # 1. Profile
    print("--- Fetch Profile ---")
    url = f"{API_URL}/chat/fetchProfile/{INSTANCE}"
    try:
        r = requests.post(url, json={"number": jid}, headers=headers)
        print(f"Status: {r.status_code}")
        print(r.text[:500])
    except Exception as e:
        print(f"Error: {e}")

    # 2. WhatsApp Number Status
    print("--- WhatsApp Number Status ---")
    url = f"{API_URL}/chat/whatsappNumbers/{INSTANCE}"
    try:
        r = requests.post(url, json={"numbers": [jid]}, headers=headers)
        print(f"Status: {r.status_code}")
        print(r.text[:500])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_jid("556195674255")
    check_jid("556196483708")
    check_jid("556195674255@s.whatsapp.net")
    check_jid("556196483708@s.whatsapp.net")
