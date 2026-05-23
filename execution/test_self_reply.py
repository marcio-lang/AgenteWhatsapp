import requests
import json

URL = "http://localhost:3000/webhook"

def test_from_me_true():
    print("Testing fromMe=True (Bot's own message)...")
    payload = {
        "event": "messages.upsert",
        "data": {
            "key": {
                "remoteJid": "556199659695@s.whatsapp.net",
                "fromMe": True,
                "id": "BOT_ID_123"
            },
            "message": {
                "conversation": "Eu sou o bot"
            }
        }
    }
    try:
        r = requests.post(URL, json=payload, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        if "ignored" in r.text and "fromMe" in r.text:
            print("PASS: Correctly ignored own message.")
        else:
            print("FAIL: Did not ignore own message.")
    except Exception as e:
        print(f"Error: {e}")

def test_from_me_false():
    print("\nTesting fromMe=False (User message)...")
    payload = {
        "event": "messages.upsert",
        "data": {
            "key": {
                "remoteJid": "556199659695@s.whatsapp.net",
                "fromMe": False,
                "id": "USER_ID_123"
            },
            "message": {
                "conversation": "Olá"
            }
        }
    }
    try:
        r = requests.post(URL, json=payload, timeout=5)
        print(f"Status: {r.status_code}")
        # Expect success but we might not have a mocked evolution client so it might error heavily on the backend, 
        # but the important part is it passes the check.
        # Since the server is running and might actually try to hit the real evolution API, 
        # we might get an error or a success depending on network.
        # But we mainly care that it DOES NOT return "ignored: fromMe".
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_from_me_true()
    test_from_me_false()
