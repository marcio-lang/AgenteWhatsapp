import urllib.request

try:
    print("Fetching http://localhost:3000/...")
    with urllib.request.urlopen("http://localhost:3000/") as response:
        html = response.read().decode('utf-8')
        print(f"HTML size: {len(html)}")
        print(f"HTML contains section-agente: {'section-agente' in html}")
        
    print("\nFetching http://localhost:3000/app.js...")
    with urllib.request.urlopen("http://localhost:3000/app.js") as response:
        js = response.read().decode('utf-8')
        print(f"JS size: {len(js)}")
        print(f"JS contains fileListContainer: {'fileListContainer' in js}")
        # Print where fileListContainer is declared to verify
        lines = js.splitlines()
        for idx, line in enumerate(lines):
            if 'fileListContainer' in line:
                print(f"Line {idx+1}: {line}")
                
    print("\nFetching http://localhost:3000/style.css...")
    with urllib.request.urlopen("http://localhost:3000/style.css") as response:
        css = response.read().decode('utf-8')
        print(f"CSS size: {len(css)}")
        print(f"CSS contains content-section: {'content-section' in css}")
except Exception as e:
    print(f"Error: {e}")
