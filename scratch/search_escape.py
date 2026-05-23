with open("frontend/app.js", "r", encoding="utf-8") as f:
    js_content = f.read()

import re
matches = list(re.finditer(r'\bescapeHtml\b', js_content))
print(f"Found {len(matches)} occurrences of escapeHtml")
for match in matches:
    start = max(0, match.start() - 50)
    end = min(len(js_content), match.end() + 50)
    print(f"Occurrence: ...{js_content[start:end]}...")
