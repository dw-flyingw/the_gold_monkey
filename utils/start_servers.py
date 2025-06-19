#!/usr/bin/env python3
"""
Start all MCP servers for Salty
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def start_server(server_name, script_path):
    """Start a single MCP server"""
    try:
        print(f"Starting {server_name} server...")
        process = subprocess.Popen([
            "uv", "run", "mcp", "run", script_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"Error starting {server_name}: {e}")
        return None

def main():
    """Start all MCP servers"""
    servers = {
        "TP-Link": "mcp_servers/tplink_server.py",
        "RAG": "mcp_servers/rag_server.py",
        "Spotify": "mcp_servers/spotify_server.py",
        "Roku": "mcp_servers/roku_server.py",
        "SaltyBot": "mcp_servers/saltybot_server.py"
    }
    
    processes = {}
    
    print("🚀 Starting all MCP servers for Salty...")
    print("=" * 50)
    
    # Start all servers
    for server_name, script_path in servers.items():
        if Path(script_path).exists():
            process = start_server(server_name, script_path)
            if process:
                processes[server_name] = process
                print(f"✅ {server_name} server started (PID: {process.pid})")
            else:
                print(f"❌ Failed to start {server_name} server")
        else:
            print(f"❌ {script_path} not found")
    
    print("=" * 50)
    print(f"🎉 Started {len(processes)} servers")
    print("\nServers are running in the background.")
    print("Press Ctrl+C to stop all servers.")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all servers...")
        for server_name, process in processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {server_name} server stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ {server_name} server force killed")
            except Exception as e:
                print(f"❌ Error stopping {server_name}: {e}")
        
        print("👋 All servers stopped. Goodbye!")

if __name__ == "__main__":
    main() 