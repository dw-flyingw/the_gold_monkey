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

def start_server(server_name, script_path, server_type="mcp"):
    """Start a single server"""
    try:
        print(f"Starting {server_name} server...")
        if server_type == "mcp":
            process = subprocess.Popen([
                "uv", "run", "mcp", "run", script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:  # standalone
            process = subprocess.Popen([
                "python3", script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"Error starting {server_name}: {e}")
        return None

def main():
    """Start all servers"""
    servers = {
        "TP-Link": {"path": "mcp_servers/tplink_server.py", "type": "mcp"},
        "RAG": {"path": "mcp_servers/rag_server.py", "type": "mcp"},
        "Spotify": {"path": "mcp_servers/spotify_server.py", "type": "mcp"},
        "Roku": {"path": "mcp_servers/roku_server.py", "type": "mcp"},
        "SaltyBot": {"path": "mcp_servers/saltybot_server.py", "type": "mcp"},
        "Voice": {"path": "mcp_servers/voice_server.py", "type": "standalone"}
    }
    
    processes = {}
    
    print("🚀 Starting all servers for Salty...")
    print("=" * 50)
    
    # Start all servers
    for server_name, server_info in servers.items():
        script_path = server_info["path"]
        server_type = server_info["type"]
        if Path(script_path).exists():
            process = start_server(server_name, script_path, server_type)
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