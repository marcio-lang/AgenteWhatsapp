import re

with open(r'c:\Users\Marcio\OneDrive\Área de Trabalho\AgenteWhatsapp\frontend\app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

lines = js_content.split('\n')
for i, line in enumerate(lines):
    if 'bc-count' in line or 'bc-fill' in line or 'bc-log' in line or 'bc-percent' in line:
        print(f"Line {i+1}: {line.strip()}")
