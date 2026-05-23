import requests
import json

URL = "http://localhost:3000/webhook"

def test_bot_own_message():
    """
    Simula o webhook que o Evolution API envia quando o BOT envia uma mensagem.
    Baseado na imagem que o usuário mostrou.
    """
    print("Testing bot's own message (fromMe=True)...")
    payload = {
        "event": "messages.upsert",
        "instance": "chat",
        "data": {
            "key": {
                "remoteJid": "556199659695@s.whatsapp.net",  # Número do bot
                "fromMe": True,  # Mensagem enviada PELO bot
                "id": "TEST_BOT_MESSAGE_ID"
            },
            "pushName": "Tecnologia Caíque",
            "message": {
                "conversation": "Olá, tudo bem?\\nO que podemos fazer por você hoje?"
            }
        },
        "sender": "556199659695@s.whatsapp.net"  # Sender é o próprio bot
    }
    
    try:
        r = requests.post(URL, json=payload, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if "ignored" in r.text.lower() and "fromme" in r.text.lower():
            print("✅ PASS: Bot's own message correctly ignored (fromMe=True)")
        else:
            print("❌ FAIL: Bot processed its own message!")
    except Exception as e:
        print(f"Error: {e}")

def test_bot_message_with_sender_none():
    """
    Testa o caso onde Evolution API envia fromMe=False mas sender=None
    (que é o safeguard que adicionamos)
    """
    print("\n\nTesting bot message with sender=None (fromMe=False)...")
    payload = {
        "event": "messages.upsert",
        "instance": "chat",
        "data": {
            "key": {
                "remoteJid": "556199659695@s.whatsapp.net",
                "fromMe": False,  # Incorretamente marcado como False
                "id": "TEST_SENDER_NONE_ID"
            },
            "message": {
                "conversation": "Olá, tudo bem?"
            }
        },
        "sender": None  # Sender é None (nosso safeguard)
    }
    
    try:
        r = requests.post(URL, json=payload, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if "ignored" in r.text.lower() and "no_sender" in r.text.lower():
            print("✅ PASS: Message with sender=None correctly ignored")
        else:
            print("❌ FAIL: Message with sender=None was processed!")
    except Exception as e:
        print(f"Error: {e}")

def test_real_user_message():
    """
    Testa mensagem de um usuário real (deve ser processada)
    """
    print("\n\nTesting real user message (should be processed)...")
    payload = {
        "event": "messages.upsert",
        "instance": "chat",
        "data": {
            "key": {
                "remoteJid": "5561999999999@s.whatsapp.net",  # Outro número
                "fromMe": False,
                "id": "TEST_USER_MESSAGE_ID"
            },
            "pushName": "Test User",
            "message": {
                "conversation": "1"
            }
        },
        "sender": "5561999999999@s.whatsapp.net"
    }
    
    try:
        r = requests.post(URL, json=payload, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if "success" in r.text.lower():
            print("✅ PASS: User message processed correctly")
        else:
            print("⚠️  WARNING: User message might not have been processed")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_bot_own_message()
    test_bot_message_with_sender_none()
    test_real_user_message()
    
    print("\n\n=== SUMMARY ===")
    print("If all tests pass, the bot should NOT respond to its own messages.")
