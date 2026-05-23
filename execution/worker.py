import os
import redis
import platform
from rq import Worker, Queue, SimpleWorker
from dotenv import load_dotenv

load_dotenv()

listen = ['default']

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

def start_worker():
    conn = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=REDIS_DB, 
        password=REDIS_PASSWORD
    )
    
    print(f"Iniciando Worker RQ conectado ao Redis em {REDIS_HOST}:{REDIS_PORT}...")
    
    # Passando a conexão explicitamente
    queue = Queue('default', connection=conn)
    
    # No Windows, usamos SimpleWorker para evitar erro de os.fork()
    if platform.system() == 'Windows':
        print("[AVISO] Detectado Windows: Usando SimpleWorker (sem fork).")
        worker = SimpleWorker([queue], connection=conn)
    else:
        worker = Worker([queue], connection=conn)
        
    worker.work()

if __name__ == '__main__':
    start_worker()
