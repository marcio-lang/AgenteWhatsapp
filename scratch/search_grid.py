import re

with open(r'c:\Users\Marcio\OneDrive\Área de Trabalho\AgenteWhatsapp\frontend\style.css', 'r', encoding='utf-8') as f:
    style_content = f.read()

lines = style_content.split('\n')
for i, line in enumerate(lines):
    if 'dashboard-grid' in line or 'dashboard-container' in line or '.content-section' in line or '.main-content' in line:
        print(f"Line {i+1}: {line.strip()}")
        for j in range(max(0, i-2), min(len(lines), i+15)):
            print(f"  {j+1}: {lines[j].rstrip()}")
        print("-" * 50)
