from execution.database_pg import get_all_chats
import json
import datetime

chats = get_all_chats()
print(f"Chats encontrados: {len(chats)}")

if chats:
    primeiro = chats[0]
    print("Exemplo de chat:", primeiro)
    print("Tipo do timestamp:", type(primeiro.get('last_time')))
    
    # Tentar serializar com json puro pra ver se quebra
    try:
        json.dumps(primeiro, default=str) # Flask jsonify usa default=str ou similar? Não, ele usa cls=JSONEncoder
        print("Serialização JSON (com default=str): OK")
    except Exception as e:
        print(f"Serialização JSON falhou: {e}")
