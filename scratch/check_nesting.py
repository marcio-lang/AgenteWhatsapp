import re

def analyze_html(filepath):
    print(f"Analyzing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    stack = []
    errors = 0
    
    for line_num, line in enumerate(lines, 1):
        matches = list(re.finditer(r'<div[^>]*>|</div>', line))
        for m in matches:
            token = m.group(0)
            if token.startswith('<div'):
                id_match = re.search(r'id=["\']([^"\']+)["\']', token)
                class_match = re.search(r'class=["\']([^"\']+)["\']', token)
                name = "div"
                if id_match:
                    name += f"#{id_match.group(1)}"
                if class_match:
                    name += f".{class_match.group(1).replace(' ', '.')}"
                stack.append((name, line_num))
            else:
                if stack:
                    stack.pop()
                else:
                    print(f"Error: Extra </div> at line {line_num}")
                    errors += 1
    
    print("\n--- Remaining Open Divs in Stack ---")
    if not stack:
        print("None! All divs are balanced.")
    else:
        for name, line_num in stack:
            print(f"Open: {name} (opened at line {line_num})")
            errors += 1
            
    print(f"\nTotal Errors/Discrepancies found: {errors}")

if __name__ == '__main__':
    analyze_html('frontend/index.html')
