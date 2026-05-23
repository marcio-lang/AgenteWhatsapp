import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("EVOLUTION_API_URL")
api_key = os.getenv("EVOLUTION_API_KEY")

print(f"EVOLUTION_API_URL: {url}")
print(f"EVOLUTION_API_KEY: {api_key}")

if "/instance/" in url:
    parts = url.split("/instance/")
    base_url = parts[0]
    instance_name = parts[1].strip("/")
else:
    base_url = url
    instance_name = "chat"

headers = {
    "apikey": api_key,
    "Content-Type": "application/json"
}

status_url = f"{base_url}/instance/connectionState/{instance_name}"
print(f"Checking connection state at: {status_url}")
try:
    r = requests.get(status_url, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Failed to check status: {e}")
