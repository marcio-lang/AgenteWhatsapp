import requests
import json

url = "http://10.0.4.119:8080"
api_key = "429683C4C977415CAAFCCE10F7D57E11"
instance_name = "chat"

headers = {
    "apikey": api_key,
    "Content-Type": "application/json"
}

print(f"Checking connection status for '{instance_name}'...")
try:
    r = requests.get(f"{url}/instance/connectionStatus/{instance_name}", headers=headers)
    print(f"Status: {r.status_code}")
    print(f"JSON: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"Failed: {e}")

print(f"\nFetching instance details...")
try:
    r = requests.get(f"{url}/instance/fetchInstances", headers=headers)
    print(f"Status: {r.status_code}")
    instances = r.json()
    if isinstance(instances, list):
        for inst in instances:
            if inst.get('name') == instance_name:
                print(f"Details for {instance_name}: {json.dumps(inst, indent=2)}")
    else:
        print(f"Response: {json.dumps(instances, indent=2)}")
except Exception as e:
    print(f"Failed: {e}")
