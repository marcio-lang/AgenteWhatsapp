with open(r'C:\Users\Marcio\.gemini\antigravity\brain\32fbd9d6-d347-4cde-a56b-e66f7f4542ad\.system_generated\tasks\task-79.log', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f"Total lines in log: {len(lines)}")
for line in lines[-100:]:
    print(line.rstrip())
