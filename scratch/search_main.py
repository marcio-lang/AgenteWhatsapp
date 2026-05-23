with open("execution/webhook_server.py", "r", encoding="utf-8") as f:
    code = f.read()

for i, line in enumerate(code.splitlines()):
    if "/api/flows" in line:
        print(f"webhook_server.py:{i+1}: {line}")
