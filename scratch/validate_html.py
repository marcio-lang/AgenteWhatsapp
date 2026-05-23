from html.parser import HTMLParser
import sys

class HTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.ignore_tags = {'meta', 'link', 'br', 'hr', 'img', 'input'}

    def handle_starttag(self, tag, attrs):
        if tag in self.ignore_tags:
            return
        # Get line number
        lineno, _ = self.getpos()
        # Find id or class if any
        id_val = None
        class_val = None
        for name, value in attrs:
            if name == 'id':
                id_val = value
            elif name == 'class':
                class_val = value
        
        desc = tag
        if id_val:
            desc += f"#{id_val}"
        if class_val:
            desc += f".{class_val.replace(' ', '.')}"
            
        self.stack.append((tag, desc, lineno))

    def handle_endtag(self, tag):
        if tag in self.ignore_tags:
            return
        
        lineno, _ = self.getpos()
        if not self.stack:
            self.errors.append(f"Line {lineno}: Closed </{tag}> but stack is empty")
            return
            
        expected_tag, expected_desc, start_line = self.stack[-1]
        if expected_tag == tag:
            self.stack.pop()
        else:
            # Let's find if the matching tag is further up in the stack
            found = False
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    found = True
                    # Report what we are closing and what we skipped
                    skipped = [self.stack[j][1] for j in range(len(self.stack) - 1, i, -1)]
                    self.errors.append(
                        f"Line {lineno}: Closed </{tag}> (opened on line {self.stack[i][2]}) "
                        f"but expected </{expected_tag}> (opened on line {start_line}). "
                        f"Skipped unclosed: {', '.join(skipped)}"
                    )
                    self.stack = self.stack[:i]
                    break
            if not found:
                self.errors.append(f"Line {lineno}: Closed </{tag}> but no matching opening tag was found in stack")

def validate(filepath):
    print(f"Validating {filepath} with HTMLParser...")
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    parser = HTMLValidator()
    parser.feed(html_content)
    
    if parser.errors:
        print("\n--- ERRORS FOUND ---")
        for err in parser.errors:
            print(err)
    else:
        print("\nNo mismatch errors found!")
        
    if parser.stack:
        print("\n--- UNCLOSED TAGS IN STACK ---")
        for tag, desc, lineno in reversed(parser.stack):
            print(f"Unclosed <{desc}> opened on line {lineno}")
    else:
        print("\nNo unclosed tags left in stack.")
        
    print(f"\nTotal Errors: {len(parser.errors) + len(parser.stack)}")

if __name__ == '__main__':
    validate('frontend/index.html')
