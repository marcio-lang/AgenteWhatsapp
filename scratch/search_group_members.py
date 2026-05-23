with open("frontend/app.js", "r", encoding="utf-8") as f:
    js_content = f.read()

import re

def print_function(func_name):
    print(f"=== FUNCTION {func_name} ===")
    pattern = rf"(async\s+)?function\s+{func_name}\b.*?(\{{|\n)"
    match = re.search(pattern, js_content)
    if not match:
        print(f"Could not find function {func_name} definition via regex.")
        return
    
    start_pos = match.start()
    # Find matching brace
    brace_count = 0
    started = False
    for i in range(start_pos, len(js_content)):
        char = js_content[i]
        if char == '{':
            brace_count += 1
            started = True
        elif char == '}':
            brace_count -= 1
        if started and brace_count == 0:
            print(js_content[start_pos:i+1])
            break

print_function("loadContactsGroupMembers")
