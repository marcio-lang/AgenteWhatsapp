with open("frontend/app.js", "r", encoding="utf-8") as f:
    js_content = f.read()

for i, line in enumerate(js_content.splitlines()):
    if "function fetchInstanceStatus" in line:
        print(f"fetchInstanceStatus found at line {i+1}")
