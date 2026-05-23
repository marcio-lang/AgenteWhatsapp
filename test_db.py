import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "agente_whatsapp")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")

print(f"Tentando conectar em: {DB_HOST}:{DB_PORT} (User: {DB_USER}, DB: {DB_NAME})")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=5
    )
    print("✅ CONEXÃO BEM SUCEDIDA!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"📦 Versão do PostgreSQL: {version[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ FALHA NA CONEXÃO: {e}")
    print("\nDICA: Verifique se o arquivo .env está configurado corretamente com as credenciais da sua VPS.")
