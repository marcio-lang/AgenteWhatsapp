import requests
import time

url = "http://10.0.4.119:8080" # Base URL
api_key = "429683C4C977415CAAFCCE10F7D57E11"

headers = {
    "apikey": api_key,
    "Content-Type": "application/json"
}

print(f"Testing connectivity to {url}...")

# Test 1: Simple Connection (Socket check)
try:
    print("\n[Test 1] Fetching Instance Status...")
    start = time.time()
    # Using 'connect' endpoint usually is fast
    r = requests.get(f"{url}/instance/connect/chat", headers=headers, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Time: {time.time() - start:.2f}s")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Test 1 Failed: {e}")

# Test 2: Send Text (The one failing)
try:
    print("\n[Test 2] Sending Test Message...")
    payload = {
        "number": "556199659695", # The number from your logs
        "text": "Connectivity Test",
        "delay": 1200,
        "linkPreview": True
    }
    start = time.time()
    r = requests.post(f"{url}/message/sendText/chat", json=payload, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Time: {time.time() - start:.2f}s")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Test 2 Failed: {e}")
