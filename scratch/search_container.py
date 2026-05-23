import re

with open(r'c:\Users\Marcio\OneDrive\Área de Trabalho\AgenteWhatsapp\frontend\style.css', 'r', encoding='utf-8') as f:
    style_content = f.read()

lines = style_content.split('\n')
for i, line in enumerate(lines):
    if 'section-' in line:
        print(f"Line {i+1}: {line.strip()}")
