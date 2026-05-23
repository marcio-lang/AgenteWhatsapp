with open(r'c:\Users\Marcio\OneDrive\Área de Trabalho\AgenteWhatsapp\frontend\app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# let's look at the very end of app.js where DOMContentLoaded ends, or initialization functions
print("First 10 lines of app.js:")
for i in range(15):
    print(f"  {i+1}: {lines[i].rstrip()}")

print("\nLast 150 lines of app.js:")
for i in range(len(lines) - 150, len(lines)):
    print(f"  {i+1}: {lines[i].rstrip()}")
