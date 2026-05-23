import requests
import json

url = "http://10.0.4.119:8080"
instance = "chat"
api_key = "429683C4C977415CAAFCCE10F7D57E11"
lid = "135768261533797@lid"

headers = {
    "apikey": api_key,
    "Content-Type": "application/json"
}

session = requests.Session()
session.trust_env = False

print(f"Attempting to resolve LID: {lid}")

# Test 1: Check WhatsApp (Might return the real JID)
print("\n[Test 1] POST /chat/whatsappNumbers")
try:
    r = session.post(f"{url}/chat/whatsappNumbers/{instance}", json={"numbers": ["135768261533797"]}, headers=headers)
    try:
        print(json.dumps(r.json(), indent=2))
    except:
        print(r.text)
except Exception as e:
    print(e)

# Test 2: Find Contact
print("\n[Test 2] POST /chat/findContacts")
try:
    # Just print raw text, keep it short
    r = session.post(f"{url}/chat/findContacts/{instance}", json={"where": {"id": lid}}, headers=headers)
    print(r.text[:500]) # Limit output to avoid truncation
except Exception as e:
    print(e)
