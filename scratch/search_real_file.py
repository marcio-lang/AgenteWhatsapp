with open("frontend/app.js", "r", encoding="utf-8") as f:
    js_content = f.read()

import re
print("Matches for real-file:")
for m in re.finditer(r'real-file', js_content):
    print(js_content[max(0, m.start()-50):min(len(js_content), m.end()+50)])
print("Matches for realFileList:")
for m in re.finditer(r'realFileList', js_content):
    print(js_content[max(0, m.start()-50):min(len(js_content), m.end()+50)])
