import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

print(f"Tentando conectar ao Redis em: {REDIS_HOST}:{REDIS_PORT}")

try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        socket_connect_timeout=5
    )
    
    # Tenta um comando simples
    r.ping()
    print("✅ CONEXÃO REDIS BEM SUCEDIDA!")
    print(f"Info do Redis: {r.info()['redis_version']}")
    
except Exception as e:
    print(f"❌ FALHA NA CONEXÃO REDIS: {e}")
    print("\nDICA: Verifique se o 'bind' no redis.conf está 0.0.0.0 e se a porta 6379 está liberada.")
