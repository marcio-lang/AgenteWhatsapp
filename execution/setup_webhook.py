import os
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

API_URL = os.getenv("EVOLUTION_API_URL")
API_KEY = os.getenv("EVOLUTION_API_KEY")

if not API_URL or not API_KEY:
    print("Error: EVOLUTION_API_URL or EVOLUTION_API_KEY not found in .env")
    exit(1)

# Helper to get instance name
def get_instance_name(url):
    parts = url.split('/')
    if 'instance' in parts:
        idx = parts.index('instance')
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return "AgenteWhatsapp" # Default fallback if not found

INSTANCE_NAME = get_instance_name(API_URL)

# If the URL already ends with /instance/NAME, we might need to strip it to get base url
# OR we just use the API_URL if it's the base
# Commonly: Base URL = server.com/
# Instance URL = server.com/instance/NAME
# The endpoint to set webhook is: /webhook/set/NAME

# Let's try to construct the correct endpoint
# If API_URL is https://10.0.4.119:8080/instance/AgenteWhatsapp
# We want https://10.0.4.119:8080/webhook/set/AgenteWhatsapp

# Logic to handle both base URL and instance URL
if "/instance/" in API_URL:
    # Split to get base and instance
    parts = API_URL.split("/instance/")
    BASE_URL = parts[0]
    INSTANCE_NAME = parts[1].strip("/")
else:
    BASE_URL = API_URL
    # Default to 'chat' if not found, or prompt user? 
    # Let's assume 'chat' based on user input
    if INSTANCE_NAME == "AgenteWhatsapp": # Old default
         INSTANCE_NAME = "chat"

if BASE_URL.endswith('/'):
    BASE_URL = BASE_URL[:-1]

WEBHOOK_ENDPOINT = f"{BASE_URL}/webhook/set/{INSTANCE_NAME}"

print(f"--- Configuration ---")
print(f"Instance: {INSTANCE_NAME}")
print(f"Base API: {BASE_URL}")
print(f"Target:   {WEBHOOK_ENDPOINT}")
print(f"---------------------")

# Our local IP where the script is running (User to input or auto-detect?)
# For simplicity, we ask the user or assume they know to change it if running externally.
# We will try to detect local IP
import socket
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()
WEBHOOK_URL = f"http://{LOCAL_IP}:3000/webhook"

print(f"Setting Webhook URL to: {WEBHOOK_URL}")

payload = {
    "webhook": {
        "url": WEBHOOK_URL,
        "enabled": True,
        "events": ["MESSAGES_UPSERT"],
        "webhookByEvents": False
    }
}

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

try:
    response = requests.post(WEBHOOK_ENDPOINT, json=payload, headers=headers, verify=False) # verify=False for local SSL
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("✅ Webhook configured successfully!")
    else:
        print("❌ Failed to configure webhook.")
        
except Exception as e:
    print(f"Error: {e}")
