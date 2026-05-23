import re

with open("frontend/app.js", "r", encoding="utf-8") as f:
    js_content = f.read()

print("Query selectors:")
for i, line in enumerate(js_content.splitlines()):
    if "querySelector" in line:
        print(f"{i+1}: {line}")
