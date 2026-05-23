import datetime

def log_message(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("server.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")
