import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("EVOLUTION_API_URL").split("/instance/")[0]
API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE = "chat"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def check_jid(jid):
    print(f"\n--- Checking {jid} ---")
    # 1. Try to find contact (using plural findContacts as in evolution_api.py)
    url = f"{API_URL}/chat/findContacts/{INSTANCE}"
    payload = {"where": {"id": jid}}
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"Find Contact: {r.status_code}")
        try:
            print(json.dumps(r.json(), indent=2))
        except:
            print(r.text[:500])
    except Exception as e:
        print(f"Error finding contact: {e}")

    # 2. Try to fetch profile
    url = f"{API_URL}/chat/fetchProfile/{INSTANCE}"
    payload = {"number": jid}
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"Fetch Profile: {r.status_code}")
        try:
            print(json.dumps(r.json(), indent=2))
        except:
            print(r.text[:500])
    except Exception as e:
        print(f"Error fetching profile: {e}")

if __name__ == "__main__":
    # Test both numbers
    check_jid("556195674255@s.whatsapp.net")
    check_jid("556196483708@s.whatsapp.net")
