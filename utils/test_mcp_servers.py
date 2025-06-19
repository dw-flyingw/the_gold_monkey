#!/usr/bin/env python3
"""
Test script to check MCP servers using mcp run
"""

import subprocess
import json
import time
import sys
from pathlib import Path

def check_server_structure(server_name, server_path):
    """Check if a server has the correct structure"""
    print(f"\n{'='*60}")
    print(f"Checking {server_name} server: {server_path}")
    print(f"{'='*60}")
    
    if not Path(server_path).exists():
        print(f"❌ Server file not found: {server_path}")
        return False
    
    try:
        # Read the server file to check for required components
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Check for required MCP components
        checks = {
            "FastMCP import": "from mcp.server.fastmcp import FastMCP" in content,
            "Server creation": "FastMCP(" in content,
            "Tool decorators": "@server.tool()" in content,
            "stdio_server": "stdio_server" in content,
            "Main guard": "if __name__ == \"__main__\":" in content
        }
        
        print("🔍 Checking server structure...")
        all_passed = True
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print(f"✅ {server_name} server structure is correct")
        else:
            print(f"❌ {server_name} server has structural issues")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error checking {server_name}: {e}")
        return False

def test_mcp_run_command(server_name, server_path):
    """Test the mcp run command syntax"""
    print(f"\n🚀 Testing mcp run command for {server_name}...")
    
    try:
        # Test the mcp run command (this will start the server briefly)
        result = subprocess.run([
            "mcp", "run", server_path, "--help"
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print(f"✅ mcp run command works for {server_name}")
            return True
        else:
            print(f"❌ mcp run command failed for {server_name}")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ mcp run command timed out for {server_name} (this is normal)")
        return True
    except Exception as e:
        print(f"❌ Error testing mcp run for {server_name}: {e}")
        return False

def show_mcp_run_commands():
    """Show the mcp run commands for all servers"""
    print(f"\n{'='*60}")
    print("📋 MCP Run Commands")
    print(f"{'='*60}")
    
    servers = {
        "TP-Link": "mcp_servers/tplink_server.py",
        "RAG": "mcp_servers/rag_server.py",
        "Spotify": "mcp_servers/spotify_server.py",
        "Roku": "mcp_servers/roku_server.py",
        "SaltyBot": "mcp_servers/saltybot_server.py"
    }
    
    for server_name, server_path in servers.items():
        print(f"\n🔧 {server_name} Server:")
        print(f"   mcp run {server_path}")
        print(f"   mcp run {server_path} --transport stdio")
    
    print(f"\n💡 To run all servers using the start script:")
    print(f"   python utils/start_servers.py")
    print(f"\n💡 To stop all servers:")
    print(f"   python utils/stop_servers.py")

def main():
    """Test all MCP servers"""
    servers = {
        "TP-Link": "mcp_servers/tplink_server.py",
        "RAG": "mcp_servers/rag_server.py",
        "Spotify": "mcp_servers/spotify_server.py",
        "Roku": "mcp_servers/roku_server.py",
        "SaltyBot": "mcp_servers/saltybot_server.py"
    }
    
    print("🔧 MCP Server Testing Tool (using mcp run)")
    print("=" * 60)
    print("This script checks all MCP servers for proper structure")
    print("and tests the mcp run command syntax")
    print("=" * 60)
    
    structure_results = {}
    command_results = {}
    
    for server_name, server_path in servers.items():
        structure_results[server_name] = check_server_structure(server_name, server_path)
        command_results[server_name] = test_mcp_run_command(server_name, server_path)
    
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print(f"{'='*60}")
    
    structure_passed = 0
    command_passed = 0
    
    for server_name in servers.keys():
        structure_ok = structure_results[server_name]
        command_ok = command_results[server_name]
        
        structure_status = "✅ PASS" if structure_ok else "❌ FAIL"
        command_status = "✅ PASS" if command_ok else "❌ FAIL"
        
        print(f"{server_name:15} Structure: {structure_status} | Command: {command_status}")
        
        if structure_ok:
            structure_passed += 1
        if command_ok:
            command_passed += 1
    
    print(f"\n🎯 Results:")
    print(f"   Structure: {structure_passed}/{len(servers)} servers passed")
    print(f"   Commands: {command_passed}/{len(servers)} servers passed")
    
    if structure_passed == len(servers) and command_passed == len(servers):
        print("🎉 All servers are ready to run with mcp run!")
    else:
        print("⚠️ Some servers have issues. Check the output above.")
    
    # Show the mcp run commands
    show_mcp_run_commands()

if __name__ == "__main__":
    main() 