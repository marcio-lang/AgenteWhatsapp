import re

with open(r'c:\Users\Marcio\OneDrive\Área de Trabalho\AgenteWhatsapp\frontend\app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'fetchInstanceStatus' in line:
        print(f"{i+1}: {line.strip()}")
        for j in range(max(0, i-2), min(len(lines), i+30)):
            print(f"  {j+1}: {lines[j].rstrip()}")
        break
