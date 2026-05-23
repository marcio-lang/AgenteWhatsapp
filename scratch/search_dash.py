with open("execution/database_pg.py", "r", encoding="utf-8") as f:
    code = f.read()

lines = code.splitlines()
start = -1
for i, line in enumerate(lines):
    if "def get_db_connection" in line:
        start = i
        break

if start != -1:
    for j in range(start, min(start + 45, len(lines))):
        print(f"{j+1}: {lines[j]}")
