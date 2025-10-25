#!/usr/bin/env python3
import json
import subprocess
import time

mcp = subprocess.Popen(['npx', '@playwright/mcp'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
time.sleep(3)

# Test simple evaluate
test_code = '''
() => {
    return JSON.stringify({
        test: 'hello',
        numbers: [1, 2, 3]
    });
}
'''

request = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'tools/call',
    'params': {'name': 'browser_evaluate', 'arguments': {'function': test_code}}
}

mcp.stdin.write(json.dumps(request) + '\n')
mcp.stdin.flush()
time.sleep(2)

result = mcp.stdout.readline()
print("=" * 80)
print("Raw result length:", len(result))
print("=" * 80)
import pprint
data = json.loads(result)
pprint.pprint(data)

mcp.terminate()
