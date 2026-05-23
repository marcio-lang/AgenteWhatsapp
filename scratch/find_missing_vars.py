import re
import sys

# Set stdout encoding or use ascii safe print
def safe_print(text):
    print(text.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8'))

# Read app.js
with open("frontend/app.js", "r", encoding="utf-8") as f:
    content = f.read()

# Find all words that look like variables
words = set(re.findall(r'\b[a-zA-Z_]\w*\b', content))

# Find all declared variables
declared = set()
# Match declarations: const var1, let var2, var var3, function func, etc.
for m in re.finditer(r'\b(const|let|var|function|class)\s+([a-zA-Z_]\w*)', content):
    declared.add(m.group(2))

# Match function arguments: async function f(a, b) or (a, b) => or function(a)
for m in re.finditer(r'function\s*\w*\s*\(([^)]*)\)', content):
    args = m.group(1).split(',')
    for arg in args:
        name = arg.strip().split('=')[0].strip()
        if name:
            declared.add(name)

for m in re.finditer(r'\(([^)]*)\)\s*=>', content):
    args = m.group(1).split(',')
    for arg in args:
        name = arg.strip().split('=')[0].strip()
        if name:
            declared.add(name)

# Some standard globals
standard_globals = {
    'window', 'document', 'console', 'fetch', 'localStorage', 'sessionStorage',
    'Audio', 'Notification', 'alert', 'prompt', 'confirm', 'JSON', 'Set', 'Map',
    'Array', 'FormData', 'parseInt', 'parseFloat', 'Number', 'String', 'Boolean',
    'setInterval', 'clearInterval', 'setTimeout', 'clearTimeout', 'encodeURIComponent',
    'decodeURIComponent', 'Math', 'RegExp', 'Date', 'Error', 'escapeHtml', 'Object',
    'Headers', 'HeadersInit', 'Request', 'Response'
}

# Find words that are not declared and not standard globals, and check if they are used as variables
undeclared_suspects = words - declared - standard_globals

# Filter out common JS keywords
keywords = {
    'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break', 'continue',
    'return', 'try', 'catch', 'finally', 'throw', 'new', 'typeof', 'instanceof', 'void',
    'delete', 'in', 'of', 'var', 'let', 'const', 'function', 'class', 'extends', 'super',
    'this', 'true', 'false', 'null', 'undefined', 'async', 'await', 'import', 'export', 'from', 'as'
}
undeclared_suspects = undeclared_suspects - keywords

# Also filter out variable usages that are inside object properties e.g. obj.suspect or { suspect: 123 }
# We want to keep only those that are used as actual standalone identifiers in the code.
# Let's verify each suspect is used as a standalone identifier.
standalone_suspects = []
for s in undeclared_suspects:
    # Standalone identifier: not preceded by '.' or preceded by keywords, not followed by ':' if inside object literal (complex to parse, so let's just do a basic check)
    # Match standalone: not preceded by a dot
    matches = list(re.finditer(rf'(?<!\.)\b{s}\b', content))
    # Filter out if it's followed by ':' (like an object property key)
    valid_matches = []
    for m in matches:
        # Check if followed by colon (and not double colon or something)
        post = content[m.end():m.end()+10].strip()
        if post.startswith(':'):
            continue
        valid_matches.append(m)
    
    if len(valid_matches) > 0:
        standalone_suspects.append((s, valid_matches[0]))

safe_print(f"Found {len(standalone_suspects)} standalone undeclared suspects:")
for s, first in sorted(standalone_suspects, key=lambda x: x[0]):
    start = max(0, first.start() - 40)
    end = min(len(content), first.end() + 40)
    # clean newlines for nice display
    ctx = content[start:end].replace('\n', ' ')
    safe_print(f"  {s}: ...{ctx}...")
