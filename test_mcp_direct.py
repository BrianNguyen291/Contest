#!/usr/bin/env python3
"""Test Playwright MCP directly"""
import json
import subprocess
import time

# Start MCP server
mcp = subprocess.Popen(
    ['npx', '@playwright/mcp'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
time.sleep(3)

# Navigate to AA.com
request = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'tools/call',
    'params': {
        'name': 'browser_navigate',
        'arguments': {'url': 'https://www.aa.com'}
    }
}
mcp.stdin.write(json.dumps(request) + '\n')
mcp.stdin.flush()
time.sleep(5)

# Take snapshot
request = {
    'jsonrpc': '2.0',
    'id': 2,
    'method': 'tools/call',
    'params': {
        'name': 'browser_snapshot',
        'arguments': {}
    }
}
mcp.stdin.write(json.dumps(request) + '\n')
mcp.stdin.flush()
time.sleep(2)

# Read result
result = mcp.stdout.readline()
print("Snapshot result:", result[:500])

# Close
mcp.terminate()
