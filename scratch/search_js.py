import re

with open(r'c:\Users\Marcio\OneDrive\Área de Trabalho\AgenteWhatsapp\frontend\app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

functions = [
    'fetchContacts',
    'fetchFiles',
    'fetchFilesForBroadcast',
    'fetchContactGroups',
    'fetchAgentFlows',
    'updateDashboard',
    'startPolling',
    'stopPolling'
]

for func in functions:
    found = False
    for i, line in enumerate(lines):
        if re.search(r'function\s+' + func + r'\b', line) or re.search(func + r'\s*=\s*(async\s*)?\(\s*\)\s*=>', line):
            print(f"Function {func} found at line {i+1}: {line.strip()}")
            # print next 20 lines
            for j in range(max(0, i-2), min(len(lines), i+30)):
                print(f"  {j+1}: {lines[j].rstrip()}")
            found = True
            print("-" * 50)
            break
    if not found:
        print(f"Function {func} NOT found!")
