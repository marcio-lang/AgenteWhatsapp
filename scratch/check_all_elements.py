import re

# Read app.js
with open(r'c:\Users\Marcio\OneDrive\Área de Trabalho\AgenteWhatsapp\frontend\app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Read index.html
with open(r'c:\Users\Marcio\OneDrive\Área de Trabalho\AgenteWhatsapp\frontend\index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find all document.getElementById('...')
id_queries = set(re.findall(r"document\.getElementById\(['\"]([^'\"]+)['\"]\)", js_content))

# Find all IDs defined in HTML (e.g., id="some-id")
html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', html_content))

print("Checking document.getElementById:")
missing_ids = id_queries - html_ids
if missing_ids:
    print(f"FOUND {len(missing_ids)} MISSING IDs:")
    for mid in sorted(missing_ids):
        print(f"  - {mid} is queried in JS but NOT found in index.html")
else:
    print("All document.getElementById IDs exist in HTML!")

# Find all document.querySelector/querySelectorAll
selector_queries = set(re.findall(r"document\.querySelector(?:All)?\(['\"]([^'\"]+)['\"]\)", js_content))
print("\nChecking selectors:")
for sel in sorted(selector_queries):
    # Basic check for class selectors
    if sel.startswith('.'):
        class_name = sel[1:]
        # Look for class in HTML
        if class_name not in html_content:
            print(f"  - Selector '{sel}' not found in HTML (class '{class_name}')")
    elif sel.startswith('#'):
        id_name = sel[1:]
        if id_name not in html_ids:
            print(f"  - Selector '{sel}' not found in HTML (id '{id_name}')")
