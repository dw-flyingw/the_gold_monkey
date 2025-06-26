#!/usr/bin/env python3
"""
Test MCP servers using MCP CLI
"""

import subprocess
import json
import time
import sys
from pathlib import Path

def test_mcp_server_tools(server_name, server_path):
    """Test MCP server tools using mcp run"""
    print(f"\n🧪 Testing {server_name} MCP server tools...")
    print("=" * 50)
    
    try:
        # Start the server and get its tools
        process = subprocess.Popen([
            "uv", "run", "mcp", "run", server_path
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Send a tools/list request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        # Also send initialization request first
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        init_json = json.dumps(init_request) + "\n"
        tools_json = json.dumps(request) + "\n"
        
        # Send both requests
        combined_input = init_json + tools_json
        stdout, stderr = process.communicate(input=combined_input, timeout=10)
        
        if process.returncode == 0 and stdout.strip():
            try:
                # Handle multi-line JSON responses
                lines = stdout.strip().split('\n')
                tools_response = None
                
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line.strip())
                            # Look for the tools/list response
                            if response.get("id") == 1 and "result" in response:
                                tools_response = response
                                break
                        except json.JSONDecodeError:
                            continue
                
                if tools_response and "tools" in tools_response["result"]:
                    tools = tools_response["result"]["tools"]
                    print(f"✅ {server_name}: Found {len(tools)} tools")
                    for tool in tools:
                        print(f"   • {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                    return True
                else:
                    print(f"❌ {server_name}: No tools found in response")
                    print(f"   Response: {stdout[:200]}...")
                    return False
            except Exception as e:
                print(f"❌ {server_name}: Error parsing response - {e}")
                print(f"   Response: {stdout[:200]}...")
                return False
        else:
            print(f"❌ {server_name}: No response or error")
            if stderr:
                print(f"   Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {server_name}: Error - {e}")
        return False

def test_mcp_server_dev(server_name, server_path):
    """Test MCP server using mcp dev (interactive)"""
    print(f"\n🔧 Testing {server_name} with MCP Inspector...")
    print("=" * 50)
    
    try:
        # Start the server with MCP Inspector
        process = subprocess.Popen([
            "uv", "run", "mcp", "dev", server_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        if process.poll() is None:
            print(f"✅ {server_name}: MCP Inspector started successfully")
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {server_name}: MCP Inspector failed to start")
            if stderr:
                print(f"   Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {server_name}: Error - {e}")
        return False

def main():
    """Test all MCP servers"""
    servers = {
        "TP-Link": "mcp_servers/tplink_server.py",
        "RAG": "mcp_servers/rag_server.py",
        "Spotify": "mcp_servers/spotify_server.py",
        "Roku": "mcp_servers/roku_server.py",
        "SaltyBot": "mcp_servers/saltybot_server.py"
    }
    
    print("🚀 Testing MCP servers with MCP CLI...")
    print("=" * 60)
    
    tools_results = {}
    dev_results = {}
    
    # Test each server
    for server_name, server_path in servers.items():
        if Path(server_path).exists():
            # Test tools
            tools_ok = test_mcp_server_tools(server_name, server_path)
            tools_results[server_name] = tools_ok
            
            # Test dev mode
            dev_ok = test_mcp_server_dev(server_name, server_path)
            dev_results[server_name] = dev_ok
        else:
            print(f"❌ {server_name}: {server_path} not found")
            tools_results[server_name] = False
            dev_results[server_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 MCP CLI Test Results Summary")
    print(f"{'='*60}")
    
    tools_passed = 0
    dev_passed = 0
    
    for server_name in servers.keys():
        tools_ok = tools_results[server_name]
        dev_ok = dev_results[server_name]
        
        tools_status = "✅ PASS" if tools_ok else "❌ FAIL"
        dev_status = "✅ PASS" if dev_ok else "❌ FAIL"
        
        print(f"{server_name:15} Tools: {tools_status} | Dev: {dev_status}")
        
        if tools_ok:
            tools_passed += 1
        if dev_ok:
            dev_passed += 1
    
    print(f"\n🎯 Results:")
    print(f"   Tools Test: {tools_passed}/{len(servers)} servers passed")
    print(f"   Dev Test: {dev_passed}/{len(servers)} servers passed")
    
    if tools_passed == len(servers) and dev_passed == len(servers):
        print("🎉 All MCP servers are working correctly with MCP CLI!")
    else:
        print("⚠️  Some MCP servers have issues. Check the output above.")
    
    print(f"\n💡 To test a specific server interactively:")
    print(f"   uv run mcp dev mcp_servers/[server_name]_server.py")
    print(f"\n💡 To run a server directly:")
    print(f"   uv run mcp run mcp_servers/[server_name]_server.py")

if __name__ == "__main__":
    main() 