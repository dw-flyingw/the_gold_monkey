#!/usr/bin/env python3
"""
Direct MCP server test - tests actual MCP communication
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server_direct(server_name, server_path, test_tool, test_args=None):
    """Test MCP server directly using subprocess"""
    print(f"\n🧪 Testing {server_name} MCP server directly...")
    
    try:
        # Create a simple JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": test_tool,
                "arguments": test_args or {}
            }
        }
        
        # Send request to server
        process = subprocess.Popen(
            ["uv", "run", "mcp", "run", server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send the request
        request_json = json.dumps(request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        if process.returncode == 0 and stdout.strip():
            print(f"✅ {server_name}: Server responded")
            return True
        else:
            print(f"❌ {server_name}: No response or error")
            if stderr:
                print(f"   Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {server_name}: Error - {e}")
        return False

async def main():
    """Test MCP servers directly"""
    print("🚀 Testing MCP servers directly...")
    print("=" * 50)
    
    # Test each server with a simple tool call
    tests = [
        ("SaltyBot", "mcp_servers/saltybot_server.py", "get_salty_personality"),
        ("RAG", "mcp_servers/rag_server.py", "get_database_stats"),
        ("Spotify", "mcp_servers/spotify_server.py", "get_playback_status"),
        ("TP-Link", "mcp_servers/tplink_server.py", "discover_tplink_devices"),
    ]
    
    results = []
    for server_name, server_path, test_tool in tests:
        success = await test_mcp_server_direct(server_name, server_path, test_tool)
        results.append((server_name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Direct MCP Test Results:")
    print("=" * 50)
    
    passed = 0
    for server_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{server_name:12} {status}")
        if success:
            passed += 1
    
    print(f"\n🎉 {passed}/{len(results)} servers responded to MCP calls!")
    
    if passed == len(results):
        print("🎊 All MCP servers are working correctly!")
    else:
        print("⚠️  Some MCP servers have communication issues.")

if __name__ == "__main__":
    asyncio.run(main()) 