import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "agente_whatsapp")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("--- 🔍 DIAGNÓSTICO DO BANCO DE DADOS ---")
    
    # 1. Contar Contatos
    cursor.execute("SELECT COUNT(*) as total FROM contacts")
    print(f"Total de Contatos: {cursor.fetchone()['total']}")
    
    # 2. Contar Mensagens
    cursor.execute("SELECT COUNT(*) as total FROM messages")
    print(f"Total de Mensagens: {cursor.fetchone()['total']}")
    
    # 3. Listar últimas mensagens
    print("\n--- Últimas 5 Mensagens ---")
    cursor.execute("SELECT timestamp, sender, content FROM messages ORDER BY timestamp DESC LIMIT 5")
    rows = cursor.fetchall()
    if not rows:
        print("(Nenhuma mensagem encontrada)")
    for row in rows:
        print(f"[{row['timestamp']}] {row['sender']}: {row['content']}")
        
    conn.close()

except Exception as e:
    print(f"❌ Erro ao conectar/ler banco: {e}")
