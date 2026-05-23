with open(r'c:\Users\Marcio\OneDrive\Área de Trabalho\AgenteWhatsapp\frontend\style.css', 'r', encoding='utf-8') as f:
    style_content = f.read()

lines = style_content.split('\n')
for i, line in enumerate(lines):
    if 'display:' in line or 'display :' in line:
        # print the selector line (usually a few lines above)
        print(f"Line {i+1}: {line.strip()}")
        start = max(0, i-4)
        for j in range(start, i+2):
            print(f"  {j+1}: {lines[j].rstrip()}")
        print("-" * 50)
