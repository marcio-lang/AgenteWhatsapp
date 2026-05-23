import subprocess
import datetime
import os

def get_python_processes():
    try:
        # Use wmic to get process info on Windows
        cmd = 'wmic process where "name=\'python.exe\' or name=\'python3.exe\'" get ProcessId,CommandLine,CreationDate /format:csv'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
        lines = output.strip().split('\n')
        
        results = []
        if len(lines) > 1:
            header = lines[0].split(',')
            for line in lines[1:]:
                if not line.strip(): continue
                parts = line.split(',')
                # WMIC CSV format: Node,CommandLine,CreationDate,ProcessId
                if len(parts) >= 4:
                    results.append({
                        'pid': parts[3],
                        'cmd': parts[1],
                        'start': parts[2]
                    })
        return results
    except Exception as e:
        return str(e)

procs = get_python_processes()
if isinstance(procs, str):
    print(f"Error: {procs}")
else:
    print(f"Found {len(procs)} python processes:")
    for p in procs:
        print(f"PID: {p['pid']} | Started: {p['start']} | Command: {p['cmd']}")
