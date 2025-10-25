#!/usr/bin/env python3
"""
Test MCP server startup
"""

import subprocess
import time
import sys

def test_mcp_server():
    """Test if MCP server can start"""
    print("🧪 Testing MCP server startup...")
    
    try:
        # Start MCP server
        print("🚀 Starting MCP server...")
        process = subprocess.Popen(
            ["npx", "@playwright/mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ MCP server started successfully")
            process.terminate()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ MCP server failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
